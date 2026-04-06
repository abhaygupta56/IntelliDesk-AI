"""
Agentic Manager - The Intelligent Core
Implements a true ReAct (Reasoning and Acting) loop to autonomously chain tools.
"""

import json
from groq import Groq
from src.core.function_registry import registry
from src.utils.logger import Logger
from config import Config

logger = Logger.get_logger("AgenticManager")


class AgenticManager:
    """True Agentic Router using Native Groq Tools & ReAct Loop"""
    
    def __init__(self):
        self.client = Groq(api_key=Config.GROQ_API_KEY)
        self.model = Config.GROQ_MODEL
        self.conversation_history = []
        self.max_iterations = 5
        self.system_prompt = {
            "role": "system",
            "content": (
                "You are IntelliDesk AI, a powerful agentic desktop assistant. "
                "You have access to a suite of system tools (opening apps, managing volume etc) and web tools. "
                "If the user asks you to do something, autonomously use your tools to fulfill the goal. "
                "You can chain multiple tools together if needed. "
                "Do NOT ask for permission to use tools if the goal is clear. "
                "Always be concise and inform the user of what you did in Hinglish or English."
            )
        }
    
    def get_history(self):
        """Get current chat history"""
        return self.conversation_history
        
    def clear_history(self):
        """Reset conversation"""
        self.conversation_history.clear()
        logger.info("Agentic history cleared")
        
    def process(self, user_input: str):
        """Main agent loop"""
        try:
            user_input = user_input.strip()
            if not user_input:
                return [{"type": "error", "response": "Please say something!", "status": "error"}]
                
            logger.info(f"Agent Goal: {user_input}")
            
            # Reset history bounds (keep system prompt and recent context)
            if len(self.conversation_history) == 0:
                self.conversation_history = [self.system_prompt]
            elif len(self.conversation_history) > 10:
                self.conversation_history = [self.system_prompt] + self.conversation_history[-8:]
                
            self.conversation_history.append({"role": "user", "content": user_input})
            
            # Fetch tools schema dynamically based on what might be needed
            tools = self._get_tools_schema(user_input)
            
            iterations = 0
            functions_executed = []
            
            # The ReAct Loop
            while iterations < self.max_iterations:
                iterations += 1
                logger.info(f"Agent Loop Iteration {iterations}...")
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.conversation_history,
                    tools=tools,
                    tool_choice="auto",
                    temperature=0.3
                )
                
                message = response.choices[0].message
                
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
