"""
Agentic Manager - The Intelligent Core
Implements a true ReAct (Reasoning and Acting) loop to autonomously chain tools.
"""

import json
import datetime
import platform
import psutil
from groq import Groq
from src.core.function_registry import registry
from src.memory.memory_engine import memory_engine
from src.utils.logger import Logger
from config import Config

logger = Logger.get_logger("AgenticManager")


class AgenticManager:
    """True Agentic Router using Native Groq Tools & ReAct Loop"""
    
    def __init__(self):
        self.client = Groq(api_key=Config.GROQ_API_KEY)
        self.model = Config.GROQ_MODEL
        self.conversation_history = []
        self.max_iterations = 10
        self.is_waiting_for_info = False
        self.system_prompt = {
            "role": "system",
            "content": (
                "You are IntelliDesk AI — a context-aware, multi-step autonomous desktop agent.\n\n"
                "You behave like a highly precise system that understands, plans, executes, and verifies tasks.\n\n"
                "CRITICAL RULES:\n"
                "1. STRICT TOOL USAGE: You must ONLY use the tools explicitly provided to you in this prompt's schema.\n"
                "2. INTENT MATCHING: Use the correct macro tools for the job (e.g. use `execute_keyboard_shortcut` with 'ctrl+c' for copying). Do NOT use completely unrelated tools.\n"
                "3. TASK COMPLETION: Once you have successfully executed the required tools, simply reply to the user with a confirmation (e.g., 'I have copied the text').\n"
                "4. ERROR RECOVERY: If a tool returns an error, do not repeat the exact same call. Try an alternative or tell the user it failed.\n\n"
                "---\n\n"
                "# 1. INTENT UNDERSTANDING\n"
                "* Clearly understand what the user wants\n"
                "* Types: SIMPLE (single-step), COMPLEX (multi-step), UNCLEAR (ask clarification)\n\n"
                "---\n\n"
                "# 2. PLANNING LAYER\n"
                "If task is COMPLEX:\n"
                "* Create a step-by-step plan internally\n"
                "* Follow steps sequentially\n"
                "* Track progress\n"
                "DO NOT execute everything at once.\n\n"
                "---\n\n"
                "# 3. EXECUTION RULES\n"
                "* Use tools only when required\n"
                "* Choose the most efficient action\n"
                "* Avoid repeating actions\n"
                "* Do not perform unnecessary steps\n\n"
                "---\n\n"
                "# 4. CONTEXT AWARENESS\n"
                "If system context is available, use it:\n"
                "Examples:\n"
                "* If app is already open -> do not reopen\n"
                "* If battery is low -> avoid heavy operations\n"
                "* If screen is relevant -> use visual analysis\n"
                "Context should influence decisions.\n\n"
                "---\n\n"
                "# 5. WORKING MEMORY (SESSION LOGIC)\n"
                "You must remember during the session:\n"
                "* Current task\n"
                "* Steps already completed\n"
                "* Previous successes/failures\n"
                "Never repeat failed actions blindly.\n\n"
                "---\n\n"
                "# 6. SELF-EVALUATION LOOP\n"
                "After every action:\n"
                "* Check if the step succeeded\n"
                "* If yes -> continue\n"
                "* If no -> try a different method\n"
                "Do not get stuck in loops.\n\n"
                "---\n\n"
                "# 7. SAFETY LAYER (STRICT)\n"
                "Never perform:\n"
                "* Destructive operations (delete files, system damage)\n"
                "* Unsafe command execution\n"
                "* Irreversible actions without strong reason\n"
                "If a request is risky:\n"
                "* Ask for confirmation or refuse\n\n"
                "---\n\n"
                "# 8. RESPONSE STYLE\n"
                "Be:\n"
                "* Concise\n"
                "* Action-oriented\n"
                "* Clear\n"
                "Do NOT over-explain internal reasoning to the user.\n\n"
                "---\n\n"
                "# 9. FAILURE HANDLING\n"
                "If task cannot be completed:\n"
                "* Try alternative approaches\n"
                "* If still failing -> explain clearly and stop\n\n"
                "---\n\n"
                "# 10. TASK COMPLETION & EXITING THE LOOP (CRITICAL)\n"
                "ONCE YOU HAVE ACHIEVED THE USER'S GOAL, YOU MUST STOP CALLING TOOLS.\n"
                "To finish the task, simply reply with a normal conversational message (e.g. 'I have opened Chrome for you.') WITHOUT generating any tool calls.\n"
                "Do NOT artificially extend the task by taking screenshots, checking the time, or running arbitrary checks unless the user specifically asked you to verify.\n\n"
                "---\n\n"
                "# 11. GOAL\n"
                "You are not here to respond like a chatbot.\n"
                "You are here to COMPLETE tasks like an intelligent system.\n"
                "Think -> Plan -> Act -> Evaluate -> Complete."
            )
        }
    
    def get_history(self):
        """Get current chat history"""
        return self.conversation_history
        
    def clear_history(self):
        """Reset conversation"""
        self.conversation_history.clear()
        self.is_waiting_for_info = False
        logger.info("Agentic history cleared")
        
    def _get_system_context(self) -> str:
        """Fetch real-time system context + long-term memory to inject into prompt"""
        try:
            current_time = datetime.datetime.now().strftime("%I:%M %p, %A, %B %d, %Y")
            os_name = platform.system() + " " + platform.release()
            battery = psutil.sensors_battery()
            batt_str = f"Battery at {battery.percent}%" if battery else "Desktop (Plugged in)"

            system_state = (
                f"[SYSTEM STATE]\n"
                f"- Time: {current_time}\n"
                f"- OS: {os_name}\n"
                f"- Power: {batt_str}\n"
                f"[/SYSTEM STATE]"
            )

            # ── Long-term memory block (may be empty on first boot) ──
            memory_ctx = memory_engine.get_memory_context()
            last_session = memory_engine.get_last_session_summary()

            parts = [system_state]
            if memory_ctx:
                parts.append(memory_ctx)
            if last_session:
                parts.append(last_session)

            return "\n\n".join(parts)

        except Exception as e:
            logger.warning(f"Could not fetch full system context: {e}")
            return "[SYSTEM STATE] Current context unavailable."
        
    def process(self, user_input: str):
        """Main agent loop"""
        self.is_waiting_for_info = False
        try:
            user_input = user_input.strip()
            if not user_input:
                return [{"type": "error", "response": "Please say something!", "status": "error"}]
                
            logger.info(f"Agent Goal: {user_input}")

            # ── Extract & store facts from this message (zero API cost) ──
            new_memories = memory_engine.process_message(user_input)
            if new_memories:
                logger.info(f"MemoryEngine: {new_memories} new fact(s) extracted")
            
            # Memory Context Window fix: Always pin the system prompt & user's original request
            if len(self.conversation_history) == 0:
                self.conversation_history = [self.system_prompt]
            elif len(self.conversation_history) > 12:
                # Keep system prompt (index 0), original user trace (index 1), and then tail messages
                # Ensuring we don't crash if length is weird somehow.
                self.conversation_history = [
                    self.conversation_history[0], 
                    self.conversation_history[1]
                ] + self.conversation_history[-10:]
                
            # Inject real-time system context + long-term memory as a separate system message
            # (NOT inside the user message — that causes the LLM to echo it back)
            system_state = self._get_system_context()
            self.conversation_history.append({
                "role": "system",
                "content": system_state
            })

            # User message stays clean — just the raw command
            self.conversation_history.append({"role": "user", "content": user_input})
            
            # Fetch tools schema dynamically based on what might be needed
            tools = self._get_tools_schema(user_input)
            
            iterations = 0
            functions_executed = []
            
            # The ReAct Loop
            while iterations < self.max_iterations:
                iterations += 1
                logger.info(f"Agent Loop Iteration {iterations}...")
                
                try:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=self.conversation_history,
                        tools=tools,
                        tool_choice="auto",
                        temperature=0.3
                    )
                    message = response.choices[0].message
                except Exception as e:
                    error_str = str(e)
                    if "failed_generation" in error_str:
                        logger.warning("Caught failed_generation. Attempting fallback parse.")
                        import re
                        # Catch both arguments and parameter-less calls
                        pattern = r"<function=(\w+)>(?:\s*(\{.*?\}))?"
                        matches = re.finditer(pattern, error_str)
                        fallback_executed = False
                        
                        for match in matches:
                            func_name = match.group(1)
                            args_str = match.group(2)
                            func_args = {}
                            if args_str:
                                try:
                                    func_args = json.loads(args_str.replace("'", '"'))
                                except Exception:
                                    pass
                                    
                            logger.info(f"Agent Tool Called (Fallback): {func_name}({func_args})")
                            result = registry.execute(func_name, **func_args)
                            functions_executed.append({
                                "function": func_name,
                                "arguments": func_args,
                                "result": result
                            })
                            fallback_executed = True
                            
                        if fallback_executed:
                            self.conversation_history.append({"role": "assistant", "content": "Action completed via fallback."})
                            return [{
                                "type": "chat",
                                "response": "Action sequence completed via fallback.",
                                "status": "success",
                                "functions_executed": functions_executed
                            }]
                    raise e

                # Check for Tool Calls
                if not message.tool_calls:
                    # Target achieved, LLM generated conversational response
                    assistant_msg = message.content or "Action completed."
                    self.conversation_history.append({"role": "assistant", "content": assistant_msg})
                    logger.info(f"Agent Output: {assistant_msg}")
                    
                    return [{
                        "type": "chat",
                        "response": assistant_msg,
                        "status": "success",
                        "functions_executed": functions_executed
                    }]
                
                # -------------------------------------------------------------
                # LLM Decided to take actions
                # -------------------------------------------------------------
                
                # We must append the tool_calls provided by the assistant exactly as given
                self.conversation_history.append({
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        } for tc in message.tool_calls
                    ]
                })
                
                # Execute each tool independently
                for tool_call in message.tool_calls:
                    func_name = tool_call.function.name
                    func_args_str = tool_call.function.arguments
                    
                    try:
                        func_args = json.loads(func_args_str) if func_args_str else {}
                    except json.JSONDecodeError:
                        func_args = {}
                        
                    if not isinstance(func_args, dict):
                        func_args = {}
                        
                    logger.info(f"Agent Tool Called: {func_name}({func_args})")
                    
                    # Native execution
                    result = registry.execute(func_name, **func_args)
                    
                    # ── Track successful tool usage for pattern learning ──
                    if isinstance(result, dict) and result.get("status") == "success":
                        # Capture meaningful detail (e.g. which app was opened)
                        detail = (
                            func_args.get("app_name")
                            or func_args.get("query")
                            or func_args.get("recipient")
                            or func_args.get("action")
                            or ""
                        )
                        memory_engine.track_tool_usage(func_name, str(detail)[:60])

                    # Intercept errors to provide ReAct reasoning hints to LLM
                    if isinstance(result, dict):
                        status = result.get("status")
                        if status in ["error", "failure"]:
                            result["suggestion_for_ai"] = "ERROR detected. Do NOT repeat the exact same tool call. Modify your parameters or try a different approach."
                        elif status == "needs_info":
                            result["instruction_for_ai"] = "STOP execution immediately. Do NOT guess or hallucinate missing information. Reply directly to the user asking for this exact information."
                            self.is_waiting_for_info = True
                    functions_executed.append({
                        "function": func_name,
                        "arguments": func_args,
                        "result": result
                    })
                    
                    # Feed the result back to the LLM immediately
                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result)
                    })
                    
            logger.warning("Max iterations reached for Agent Loop.")
            return [{
                "type": "warning",
                "response": "Max tool executions reached. I stopped to prevent infinite looping.",
                "status": "warning",
                "functions_executed": functions_executed
            }]
            
        except Exception as e:
            logger.error(f"Agentic loop crashed: {e}")
            return [{"type": "error", "response": f"System Error: {str(e)}", "status": "error"}]

    def _get_tools_schema(self, user_input: str):
        """Format the local registry securely into OpenAI/Groq schema"""
        raw_schema = registry.get_groq_schema(user_input)
        return [{"type": "function", "function": func} for func in raw_schema]

# Singleton instance
agentic_manager = AgenticManager()
