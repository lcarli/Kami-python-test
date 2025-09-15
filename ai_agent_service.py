#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import asyncio
import logging
from typing import Optional

try:
    import openai
    OPENAI_SDK_AVAILABLE = True
    logging.info("OpenAI SDK is available for Azure AI Services")
except ImportError:
    OPENAI_SDK_AVAILABLE = False
    logging.warning("OpenAI SDK not available. AI agent features will be disabled.")

# Fallback to Azure AI Inference (for AI Foundry scenarios)
try:
    from azure.ai.inference import ChatCompletionsClient
    from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage
    from azure.identity import DefaultAzureCredential
    from azure.core.credentials import AzureKeyCredential
    AI_INFERENCE_AVAILABLE = True
except ImportError:
    AI_INFERENCE_AVAILABLE = False
    logging.warning("Azure AI Inference SDK not available.")

from config import DefaultConfig


class AIAgentService:
    """
    Service for handling Azure AI agent interactions.
    This service replaces the echo functionality with intelligent AI responses.
    Supports both Azure AI Services (via OpenAI SDK) and Azure AI Foundry (via AI Inference SDK).
    """
    
    def __init__(self, config: DefaultConfig):
        self.config = config
        self.client = None
        self.is_configured = False
        self.service_type = None
        
        if self._has_required_config():
            self._initialize_ai_client()
    
    def _has_required_config(self) -> bool:
        """Check if required AI configuration is available."""
        has_config = bool(self.config.AI_ENDPOINT and self.config.AI_API_KEY)
        
        if has_config:
            logging.info(f"AI Configuration found:")
            logging.info(f"  - Endpoint: {self.config.AI_ENDPOINT}")
            logging.info(f"  - Model: {self.config.AI_MODEL_DEPLOYMENT_NAME}")
            logging.info(f"  - API Key: {'***' if self.config.AI_API_KEY else 'Not set'}")
        else:
            logging.warning("Required AI configuration is missing")
        
        return has_config
    
    def _initialize_ai_client(self):
        """Initialize Azure AI client."""
        try:
            # Determine service type based on endpoint
            if "cognitiveservices.azure.com" in self.config.AI_ENDPOINT:
                # Azure AI Services - use OpenAI SDK
                if not OPENAI_SDK_AVAILABLE:
                    raise ImportError("OpenAI SDK is required for Azure AI Services")
                
                logging.info("Using OpenAI SDK for Azure AI Services")
                self.client = openai.AzureOpenAI(
                    api_key=self.config.AI_API_KEY,
                    api_version="2024-02-01",  # Working API version
                    azure_endpoint=self.config.AI_ENDPOINT
                )
                self.service_type = "azure_ai_services"
                
            elif "services.ai.azure.com" in self.config.AI_ENDPOINT:
                # Azure AI Foundry - use AI Inference SDK with Azure AD
                if not AI_INFERENCE_AVAILABLE:
                    raise ImportError("Azure AI Inference SDK is required for AI Foundry")
                
                logging.info("Using Azure AD authentication for AI Foundry")
                credential = DefaultAzureCredential()
                self.client = ChatCompletionsClient(
                    endpoint=self.config.AI_ENDPOINT,
                    credential=credential
                )
                self.service_type = "azure_ai_foundry"
                
            else:
                # Default fallback - try AI Inference SDK with API key
                if AI_INFERENCE_AVAILABLE:
                    logging.info("Using Azure AI Inference SDK with API key")
                    credential = AzureKeyCredential(self.config.AI_API_KEY)
                    self.client = ChatCompletionsClient(
                        endpoint=self.config.AI_ENDPOINT,
                        credential=credential
                    )
                    self.service_type = "azure_ai_inference"
                else:
                    raise ImportError("No compatible SDK available")
            
            self.is_configured = True
            logging.info(f"Azure AI client initialized successfully (Type: {self.service_type})")
            
        except Exception as e:
            logging.error(f"Failed to initialize Azure AI client: {e}")
            self.is_configured = False
            
            self.is_configured = True
            logging.info("Azure AI Foundry client initialized successfully")
            
        except Exception as e:
            logging.error(f"Failed to initialize Azure AI Foundry client: {e}")
            self.is_configured = False
    
    def is_available(self) -> bool:
        """Check if AI agent services are available and configured."""
        return (OPENAI_SDK_AVAILABLE or AI_INFERENCE_AVAILABLE) and self.is_configured
    
    async def get_response(self, user_message: str, conversation_history: list = None) -> Optional[str]:
        """
        Get AI agent response for the given user message.
        
        Args:
            user_message: User's input message
            conversation_history: Previous conversation messages (optional)
            
        Returns:
            AI agent response or None if service unavailable
        """
        if not self.is_available():
            logging.warning("AI agent service not available")
            return None

        try:
            if self.service_type == "azure_ai_services":
                # Use OpenAI SDK for Azure AI Services
                return await self._get_response_openai(user_message, conversation_history)
            else:
                # Use AI Inference SDK for AI Foundry or other services
                return await self._get_response_ai_inference(user_message, conversation_history)
                
        except Exception as e:
            logging.error(f"Error getting AI agent response: {e}")
            logging.error(f"Error details:")
            logging.error(f"  - Endpoint: {self.config.AI_ENDPOINT}")
            logging.error(f"  - Model: {self.config.AI_MODEL_DEPLOYMENT_NAME}")
            logging.error(f"  - Service Type: {self.service_type}")
            logging.error(f"  - Error type: {type(e).__name__}")
            
            # Provide more specific error messages
            error_str = str(e).lower()
            if "404" in error_str or "not found" in error_str:
                logging.error("  - This likely means the model deployment name is incorrect or the endpoint is wrong")
                logging.error(f"  - Check if the model '{self.config.AI_MODEL_DEPLOYMENT_NAME}' is deployed in your Azure resource")
                logging.error("  - Verify the endpoint URL is correct")
            elif "401" in error_str or "unauthorized" in error_str:
                logging.error("  - This likely means the API key is incorrect or expired")
            elif "403" in error_str or "forbidden" in error_str:
                logging.error("  - This likely means insufficient permissions")
            
            return None

    async def _get_response_openai(self, user_message: str, conversation_history: list = None) -> Optional[str]:
        """Get response using OpenAI SDK (for Azure AI Services)."""
        messages = [
            {"role": "system", "content": """You are a helpful AI assistant bot. 
            You should provide helpful, friendly, and informative responses to user questions.
            Keep your responses concise but informative.
            If you don't know something, be honest about it.
            You are integrated with voice capabilities, so users may interact with you via text or voice."""}
        ]
        
        # Add conversation history if provided
        if conversation_history:
            for msg in conversation_history:
                if hasattr(msg, 'role') and hasattr(msg, 'content'):
                    messages.append({"role": msg.role, "content": msg.content})
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Get response from OpenAI
        response = await asyncio.to_thread(
            self.client.chat.completions.create,
            model=self.config.AI_MODEL_DEPLOYMENT_NAME,
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        
        if response.choices and len(response.choices) > 0:
            ai_response = response.choices[0].message.content
            logging.info(f"AI agent response generated for user message: {user_message[:50]}...")
            return ai_response
        else:
            logging.warning("No response generated from AI model")
            return None

    async def _get_response_ai_inference(self, user_message: str, conversation_history: list = None) -> Optional[str]:
        """Get response using AI Inference SDK (for AI Foundry)."""
        # Build messages for the conversation
        messages = [
            SystemMessage(content="""You are a helpful AI assistant bot. 
            You should provide helpful, friendly, and informative responses to user questions.
            Keep your responses concise but informative.
            If you don't know something, be honest about it.
            You are integrated with voice capabilities, so users may interact with you via text or voice.""")
        ]
        
        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add current user message
        messages.append(UserMessage(content=user_message))
        
        # Get response from AI model
        response = await asyncio.to_thread(
            self.client.complete,
            messages=messages,
            model=self.config.AI_MODEL_DEPLOYMENT_NAME,
            max_tokens=500,
            temperature=0.7
        )
        
        if response.choices and len(response.choices) > 0:
            ai_response = response.choices[0].message.content
            logging.info(f"AI agent response generated for user message: {user_message[:50]}...")
            return ai_response
        else:
            logging.warning("No response generated from AI model")
            return None
    
    async def get_fallback_response(self, user_message: str) -> str:
        """
        Get fallback response when AI service is not available.
        
        Args:
            user_message: User's input message
            
        Returns:
            Fallback response message
        """
        if not user_message.strip():
            return "I'm sorry, I didn't receive any message. Could you please try again?"
        
        # Provide helpful fallback based on common patterns
        user_lower = user_message.lower().strip()
        
        if any(greeting in user_lower for greeting in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']):
            return "Hello! I'm an AI assistant bot. AI services are currently not configured, so I'm running in basic mode. How can I help you today?"
        
        elif any(question in user_lower for question in ['how are you', 'how do you do']):
            return "I'm doing well, thank you for asking! I'm here to help you with any questions you might have."
        
        elif any(help_word in user_lower for help_word in ['help', 'what can you do', 'commands']):
            return "I'm an AI assistant bot with voice capabilities. Currently running in basic mode since AI services are not configured. I can respond to your messages and process voice commands like /voice, /voices, and /help."
        
        elif user_lower in ['/voice', '/voices', '/help']:
            # These will be handled by the bot's command handlers
            return f"Command received: {user_message}"
        
        else:
            return f"I received your message: '{user_message}'. I'd love to provide a more intelligent response, but AI services are currently not configured. Please set up Azure AI Foundry configuration to enable AI-powered responses."


class ConversationHistory:
    """
    Simple conversation history manager for maintaining context.
    """
    
    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.messages = []
    
    def add_user_message(self, message: str):
        """Add a user message to history."""
        if AI_INFERENCE_AVAILABLE:
            self.messages.append(UserMessage(content=message))
        else:
            # Fallback for when SDK is not available
            self.messages.append({"role": "user", "content": message})
        self._trim_history()
    
    def add_assistant_message(self, message: str):
        """Add an assistant message to history."""
        if AI_INFERENCE_AVAILABLE:
            from azure.ai.inference.models import AssistantMessage
            self.messages.append(AssistantMessage(content=message))
        else:
            # Fallback for when SDK is not available
            self.messages.append({"role": "assistant", "content": message})
        self._trim_history()
    
    def get_history(self) -> list:
        """Get conversation history."""
        return self.messages.copy()
    
    def clear(self):
        """Clear conversation history."""
        self.messages.clear()
    
    def _trim_history(self):
        """Trim history to max_history length."""
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]