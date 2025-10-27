import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import '../theme/terminal_theme.dart';
import '../widgets/terminal_panel.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final _messageController = TextEditingController();
  final _scrollController = ScrollController();
  final List<ChatMessage> _messages = [];
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    // Add welcome message
    _messages.add(
      ChatMessage(
        content: "Welcome to Tracker AI Chat! I can help you analyze your entries, provide insights about your patterns, and offer suggestions for improvement.\n\nWhat would you like to discuss?",
        isUser: false,
        timestamp: DateTime.now(),
      ),
    );
  }

  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _sendMessage() {
    if (_messageController.text.trim().isEmpty) return;

    final userMessage = ChatMessage(
      content: _messageController.text.trim(),
      isUser: true,
      timestamp: DateTime.now(),
    );

    setState(() {
      _messages.add(userMessage);
      _isLoading = true;
    });

    _messageController.clear();
    _scrollToBottom();

    // Simulate AI response (in real app, this would call your API)
    Future.delayed(const Duration(seconds: 2), () {
      final aiResponse = _generateAIResponse(userMessage.content);
      setState(() {
        _messages.add(aiResponse);
        _isLoading = false;
      });
      _scrollToBottom();
    });
  }

  ChatMessage _generateAIResponse(String userMessage) {
    // Simple response generation - in real app, this would call your AI service
    String response;
    
    if (userMessage.toLowerCase().contains('stress')) {
      response = """## Stress Analysis

Based on your recent entries, I notice you've been experiencing elevated stress levels. Here are some observations:

**Patterns Identified:**
- Stress levels above 7 for the past 3 days
- Work-related stress appears to be the primary factor
- Financial concerns may be contributing

**Recommendations:**
- Consider taking short breaks during work hours
- Practice deep breathing exercises
- Review your workload and prioritize tasks
- Ensure you're getting adequate sleep

Would you like me to analyze specific time periods or provide more targeted suggestions?""";
    } else if (userMessage.toLowerCase().contains('finance') || userMessage.toLowerCase().contains('money')) {
      response = """## Financial Overview

Looking at your financial data from the past month:

**Income vs Expenses:**
- Total income: \$2,450.00
- Total expenses: \$1,875.50
- Net positive: \$574.50

**Spending Categories:**
- **Highest**: Food & Dining (\$425.00)
- **Second**: Transportation (\$280.00)
- **Lowest**: Entertainment (\$95.00)

**Insights:**
✅ You're maintaining a positive cash flow
⚠️ Food expenses are 23% higher than last month
💡 Consider meal planning to reduce dining costs

Would you like a detailed breakdown of any specific category?""";
    } else {
      response = """## General Insights

I can help you with various aspects of your tracking data:

**Available Analysis:**
- 📊 **Trends**: Identify patterns in your mood, stress, and productivity
- 💰 **Finance**: Spending patterns, budget recommendations
- 🎯 **Goals**: Progress tracking and achievement analysis
- 🧘 **Wellbeing**: Stress management and mood correlation
- 📈 **Productivity**: Work pattern analysis and optimization

**Try asking me about:**
- "Show me my stress trends this week"
- "What's my spending pattern?"
- "How can I improve my productivity?"
- "Analyze my mood vs sleep correlation"

What specific aspect would you like to explore?""";
    }

    return ChatMessage(
      content: response,
      isUser: false,
      timestamp: DateTime.now(),
    );
  }

  void _scrollToBottom() {
    Future.delayed(const Duration(milliseconds: 100), () {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: TerminalTheme.backgroundBlack,
      appBar: AppBar(
        title: Text(
          '💬 AI Chat',
          style: TerminalTheme.terminalHeader,
        ),
        backgroundColor: TerminalTheme.backgroundDark,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.history),
            onPressed: () => _showChatHistory(),
          ),
        ],
      ),
      body: Column(
        children: [
          // Chat messages area
          Expanded(
            child: TerminalPanel(
              child: ListView.builder(
                controller: _scrollController,
                padding: const EdgeInsets.all(16),
                itemCount: _messages.length + (_isLoading ? 1 : 0),
                itemBuilder: (context, index) {
                  if (index == _messages.length) {
                    return _buildLoadingIndicator();
                  }
                  
                  final message = _messages[index];
                  return _buildMessageBubble(message);
                },
              ),
            ),
          ),
          
          // Input area
          _buildInputArea(),
        ],
      ),
    );
  }

  Widget _buildMessageBubble(ChatMessage message) {
    return Align(
      alignment: message.isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(12),
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.8,
        ),
        decoration: BoxDecoration(
          color: message.isUser 
              ? TerminalTheme.primaryCyan.withOpacity(0.2)
              : TerminalTheme.backgroundDark,
          border: Border.all(
            color: message.isUser 
                ? TerminalTheme.primaryCyan
                : TerminalTheme.borderGray,
          ),
          borderRadius: BorderRadius.circular(0),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (message.isUser)
              Text(
                message.content,
                style: TerminalTheme.terminalText,
              )
            else
              MarkdownBody(
                data: message.content,
                styleSheet: MarkdownStyleSheet(
                  h1: TerminalTheme.terminalHeader.copyWith(fontSize: 18),
                  h2: TerminalTheme.terminalHeader.copyWith(fontSize: 16),
                  p: TerminalTheme.terminalText,
                  strong: TerminalTheme.terminalTextBold,
                  em: TerminalTheme.terminalText.copyWith(fontStyle: FontStyle.italic),
                  code: TerminalTheme.terminalText.copyWith(
                    backgroundColor: TerminalTheme.backgroundDark,
                    fontFamily: 'monospace',
                  ),
                  listBullet: TerminalTheme.terminalText,
                ),
              ),
            const SizedBox(height: 4),
            Text(
              _formatTimestamp(message.timestamp),
              style: TerminalTheme.terminalTextDim.copyWith(fontSize: 10),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLoadingIndicator() {
    return Align(
      alignment: Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: TerminalTheme.backgroundDark,
          border: Border.all(color: TerminalTheme.borderGray),
          borderRadius: BorderRadius.circular(0),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            SizedBox(
              width: 12,
              height: 12,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                valueColor: AlwaysStoppedAnimation<Color>(TerminalTheme.primaryCyan),
              ),
            ),
            const SizedBox(width: 8),
            Text(
              'AI is thinking...',
              style: TerminalTheme.terminalTextDim,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInputArea() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: TerminalTheme.backgroundDark,
        border: Border(
          top: BorderSide(color: TerminalTheme.borderGray),
        ),
      ),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: _messageController,
              style: TerminalTheme.terminalText,
              maxLines: null,
              keyboardType: TextInputType.multiline,
              textInputAction: TextInputAction.send,
              onSubmitted: (_) => _sendMessage(),
              decoration: InputDecoration(
                hintText: 'Ask about your data, trends, or insights...',
                hintStyle: TerminalTheme.terminalTextDim,
                border: const OutlineInputBorder(),
                enabledBorder: OutlineInputBorder(
                  borderSide: BorderSide(color: TerminalTheme.borderGray),
                ),
                focusedBorder: OutlineInputBorder(
                  borderSide: BorderSide(color: TerminalTheme.primaryCyan),
                ),
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: 12,
                  vertical: 8,
                ),
              ),
            ),
          ),
          const SizedBox(width: 8),
          IconButton(
            onPressed: _isLoading ? null : _sendMessage,
            icon: const Icon(Icons.send),
            color: TerminalTheme.primaryCyan,
            disabledColor: TerminalTheme.textDim,
          ),
        ],
      ),
    );
  }

  String _formatTimestamp(DateTime timestamp) {
    return '${timestamp.hour.toString().padLeft(2, '0')}:${timestamp.minute.toString().padLeft(2, '0')}';
  }

  void _showChatHistory() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: TerminalTheme.backgroundDark,
        title: Text(
          'Chat History',
          style: TerminalTheme.terminalHeader,
        ),
        content: Text(
          'Chat history feature coming soon!\n\nYou\'ll be able to:\n• View past conversations\n• Search through chat logs\n• Export chat transcripts\n• Manage conversation threads',
          style: TerminalTheme.terminalText,
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(
              'Close',
              style: TerminalTheme.terminalText.copyWith(
                color: TerminalTheme.primaryCyan,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class ChatMessage {
  final String content;
  final bool isUser;
  final DateTime timestamp;

  ChatMessage({
    required this.content,
    required this.isUser,
    required this.timestamp,
  });
}