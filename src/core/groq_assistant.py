"""
Groq Assistant - With enhanced fallback parsing
Handles all XML formats in both errors and chat responses
"""

import json
import re
from groq import Groq
from src.core.function_registry import registry
from src.utils.logger import Logger
from config import Config

logger = Logger.get_logger("GroqAssistant")


class GroqAssistant:
    """Handles chat and function calling with comprehensive fallback parsing"""
    
    MAX_HISTORY = 3
    
    def __init__(self):
        self.client = Groq(api_key=Config.GROQ_API_KEY)
        self.model = Config.GROQ_MODEL
        self.conversation_history = []
        
        self.system_prompt = {
            "role": "system",
            "content": "You are IntelliDesk AI. Execute functions when asked, chat naturally otherwise. Be concise."
        }
        
        self.conversation_history.append(self.system_prompt)
    
    def chat(self, user_message: str):
        """Process message with comprehensive fallback parsing"""
        try:
            logger.info(f"User: {user_message}")
            
            # Auto-trim history
            if len(self.conversation_history) > self.MAX_HISTORY:
                self.conversation_history = [
                    self.conversation_history[0],
                    self.conversation_history[-1]
                ]
            
            self.conversation_history.append({"role": "user", "content": user_message})
            
            # Call Groq
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.conversation_history,
                tools=self._get_tools(user_message),
                tool_choice="auto",
                max_tokens=500,
                temperature=0.7
            )
            
            message = response.choices[0].message
            
            # ═══════════════════════════════════════════════════════════════
            # CASE 1: Normal function calls
            # ═══════════════════════════════════════════════════════════════
            if message.tool_calls:
                return self._handle_function_calls(message)
            
            # ═══════════════════════════════════════════════════════════════
            # CASE 2: Chat response - Check for XML
            # ═══════════════════════════════════════════════════════════════
            else:
                assistant_message = message.content
                
                # Check if response contains XML function calls
                if assistant_message and '<' in assistant_message and '>' in assistant_message:
                    xml_result = self._parse_xml_response(assistant_message)
                    if xml_result:
                        return xml_result
                
                # Normal chat response
                self.conversation_history.append({"role": "assistant", "content": assistant_message})
                logger.info(f"Assistant: {assistant_message}")
                return {"type": "chat", "response": assistant_message, "status": "success"}
        
        except Exception as e:
            error_str = str(e)
            logger.error(f"Groq error: {error_str}")
            
            # ═══════════════════════════════════════════════════════════════
            # CASE 3: Error with failed_generation
            # ═══════════════════════════════════════════════════════════════
            if "failed_generation" in error_str:
                return self._parse_failed_generation(error_str, user_message)
            
            return {"type": "error", "response": f"Error: {error_str}", "status": "error"}
    
    def _parse_xml_response(self, response: str):
        """
        Parse XML function calls from chat response
        Handles: <screenshot></screenshot>, <volume_up></volume_up>, etc.
        """
        try:
            func_name = None
            func_args = {}
            
            # ═══════════════════════════════════════════════════════════════
            # PATTERN 1: <FUNC_NAME></FUNC_NAME>
            # ═══════════════════════════════════════════════════════════════
            pattern1 = r"<(\w+)></\1>"
            match1 = re.search(pattern1, response)
            
            if match1:
                func_name = match1.group(1)
            
            # ═══════════════════════════════════════════════════════════════
            # PATTERN 2: <FUNC_NAME>{"args"}</FUNC_NAME>
            # ═══════════════════════════════════════════════════════════════
            if not func_name:
                pattern2 = r"<(\w+)>\s*(\{[^}]*\})\s*</\1>"
                match2 = re.search(pattern2, response)
                
                if match2:
                    func_name = match2.group(1)
                    args_str = match2.group(2).replace("'", '"')
                    
                    try:
                        func_args = json.loads(args_str)
                    except:
                        func_args = {}
            
            # ═══════════════════════════════════════════════════════════════
            # PATTERN 3: func_name></function> (partial XML)
            # ═══════════════════════════════════════════════════════════════
            if not func_name:
                pattern3 = r"(\w+)></function>"
                match3 = re.search(pattern3, response)
                
                if match3:
                    func_name = match3.group(1)
            
            # No XML function found
            if not func_name:
                return None
            
            # ═══════════════════════════════════════════════════════════════
            # EXECUTE FUNCTION
            # ═══════════════════════════════════════════════════════════════
            logger.info(f"XML parse executing: {func_name}({func_args})")
            
            result = registry.execute(func_name, **func_args)
            
            if result.get("status") == "success":
                msg = result.get("message", "Done")
                self.conversation_history.append({"role": "assistant", "content": msg})
                
                return {
                    "type": "function_call",
                    "response": msg,
                    "functions_executed": [{
                        "function": func_name,
                        "arguments": func_args,
                        "result": result
                    }],
                    "status": "success"
                }
            else:
                return {
                    "type": "error",
                    "response": result.get("message", "Failed"),
                    "status": "error"
                }
        
        except Exception as e:
            logger.error(f"XML parse error: {e}")
            return None
    
    def _parse_failed_generation(self, error_str: str, user_message: str):
        """
        Parse and execute function from failed_generation error
        Handles multiple formats:
        1. <function=name>{"args": "value"}
        2. <function=name />
        3. <function_name></function_name>
        4. <function_name>{"args"}</function_name>
        """
        try:
            logger.info("Attempting fallback parse of failed_generation...")
            
            func_name = None
            func_args = {}
            
            # ═══════════════════════════════════════════════════════════════
            # PATTERN 1: <function=FUNC_NAME>{"key": "value"}
            # ═══════════════════════════════════════════════════════════════
            pattern1 = r"<function=(\w+)>\s*(\{[^}]*\})"
            match1 = re.search(pattern1, error_str)
            
            if match1:
                func_name = match1.group(1)
                args_str = match1.group(2)
                args_str = args_str.replace("'", '"')
                
                try:
                    func_args = json.loads(args_str)
                except json.JSONDecodeError:
                    func_args = {}
            
            # ═══════════════════════════════════════════════════════════════
            # PATTERN 2: <function=FUNC_NAME />
            # ═══════════════════════════════════════════════════════════════
            if not func_name:
                pattern2 = r"<function=(\w+)\s*/>"
                match2 = re.search(pattern2, error_str)
                
                if match2:
                    func_name = match2.group(1)
                    func_args = {}
            
            # ═══════════════════════════════════════════════════════════════
            # PATTERN 3: <FUNC_NAME></FUNC_NAME>
            # ═══════════════════════════════════════════════════════════════
            if not func_name:
                pattern3 = r"<(\w+)></\1>"
                match3 = re.search(pattern3, error_str)
                
                if match3:
                    func_name = match3.group(1)
                    func_args = {}
            
            # ═══════════════════════════════════════════════════════════════
            # PATTERN 4: <FUNC_NAME>{"args"}</FUNC_NAME>
            # ═══════════════════════════════════════════════════════════════
            if not func_name:
                pattern4 = r"<(\w+)>\s*(\{[^}]*\})\s*</\1>"
                match4 = re.search(pattern4, error_str)
                
                if match4:
                    func_name = match4.group(1)
                    args_str = match4.group(2)
                    args_str = args_str.replace("'", '"')
                    
                    try:
                        func_args = json.loads(args_str)
                    except json.JSONDecodeError:
                        func_args = {}

            # ═══════════════════════════════════════════════════════════════
            # PATTERN 5: <function=FUNC_NAME> (no closing, no args)
            # ═══════════════════════════════════════════════════════════════
            if not func_name:
                pattern5 = r"<function=(\w+)>"
                match5 = re.search(pattern5, error_str)
                
                if match5:
                    func_name = match5.group(1)
                    func_args = {}
            
            # ═══════════════════════════════════════════════════════════════
            # IF NO PATTERN MATCHED
            # ═══════════════════════════════════════════════════════════════
            if not func_name:
                logger.warning(f"No pattern matched for: {error_str[:100]}")
                return {
                    "type": "error",
                    "response": "Could not understand command",
                    "status": "error"
                }
            
            # ═══════════════════════════════════════════════════════════════
            # EXECUTE FUNCTION
            # ═══════════════════════════════════════════════════════════════
            logger.info(f"Fallback executing: {func_name}({func_args})")
            
            result = registry.execute(func_name, **func_args)
            
            if result.get("status") == "error":
                return {
                    "type": "error",
                    "response": result.get("message", "Failed"),
                    "status": "error"
                }
            
            response = result.get("message", "Done")
            
            # Add to history
            self.conversation_history.append({
                "role": "assistant",
                "content": response
            })
            
            logger.info(f"Fallback success: {response}")
            
            return {
                "type": "function_call",
                "response": response,
                "functions_executed": [{
                    "function": func_name,
                    "arguments": func_args,
                    "result": result
                }],
                "status": "success"
            }
        
        except Exception as e:
            logger.error(f"Fallback parse failed: {e}")
            return {
                "type": "error",
                "response": f"Command failed: {str(e)}",
                "status": "error"
            }
    
    def _handle_function_calls(self, message):
        """Execute function calls from Groq tool_calls"""
        try:
            tool_calls = message.tool_calls
            
            self.conversation_history.append({
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in tool_calls
                ]
            })
            
            function_results = []
            
            for tool_call in tool_calls:
                func_name = tool_call.function.name
                func_args_str = tool_call.function.arguments
                
                if func_args_str.strip() in ['', '{}', 'null', 'None']:
                    func_args = {}
                else:
                    try:
                        func_args = json.loads(func_args_str)
                    except:
                        func_args = {}
                
                logger.info(f"Executing: {func_name}({func_args})")
                result = registry.execute(func_name, **func_args)
                
                function_results.append({
                    "function": func_name,
                    "arguments": func_args,
                    "result": result
                })
                
                self.conversation_history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                })
            
            assistant_message = result.get("message", "Done")
            self.conversation_history.append({"role": "assistant", "content": assistant_message})
            
            logger.info(f"Assistant: {assistant_message}")
            
            return {
                "type": "function_call",
                "response": assistant_message,
                "functions_executed": function_results,
                "status": "success"
            }
        
        except Exception as e:
            logger.error(f"Function error: {str(e)}")
            return {"type": "error", "response": f"Failed: {str(e)}", "status": "error"}
    
    def _get_tools(self, user_message: str = ""):
        """Get function schemas for Groq"""
        return [
            {"type": "function", "function": func}
            for func in registry.get_groq_schema(user_message)
        ]
    
    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = [self.system_prompt]
        logger.info("Conversation reset")
    
    def get_history(self):
        """Get conversation history"""
        return self.conversation_history