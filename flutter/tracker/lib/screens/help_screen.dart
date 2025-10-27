import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import '../theme/terminal_theme.dart';
import '../widgets/terminal_panel.dart';

class HelpScreen extends StatelessWidget {
  const HelpScreen({super.key});

  @override
  Widget build(BuildContext context) {
    const helpContent = """
# Tracker Terminal - Help Guide

Welcome to Tracker Terminal! This mobile app brings the power of command-line tracking to your fingertips with an authentic terminal interface.

## 📱 Navigation Commands

### Main Menu Navigation
- **Press 1** → New Entry - Create a new tracker entry
- **Press 2** → View Entries - Browse your recent entries  
- **Press 3** → Search - Search entries by date or text
- **Press 4** → AI Chat - Chat with AI about your data
- **Press 5** → Statistics - View tracking analytics
- **Press 6** → Profile - Manage your profile settings
- **Press 7** → Export - Export your data
- **Press 8** → Achievements - View your achievements
- **Press 9** → Settings - App preferences
- **Press h** → Help - This help screen
- **Press 0** → About - App information

## 📝 Entry Types

### Daily Entries Include:
- **Finance**: Income, expenses, budget tracking
- **Work**: Productivity, notes, accomplishments  
- **Wellbeing**: Stress levels (1-10), mood tracking
- **Journal**: Personal reflections and thoughts

### Quick Entry vs Full Entry
- **Quick Entry**: Basic finance and mood data only
- **Full Entry**: Complete data across all categories

## 🔍 Search Features

### Text Search
- Search through entry notes and descriptions
- Case-insensitive matching
- Highlights matching terms

### Date Range Search  
- Select start and end dates
- View entries within specific time periods
- Combine with text search for refined results

## 💬 AI Chat Features

### What You Can Ask:
- **"Show me my stress trends this week"**
- **"Analyze my spending patterns"**  
- **"How can I improve my productivity?"**
- **"What's my mood vs sleep correlation?"**

### AI Response Types:
- **Trend Analysis**: Identifies patterns in your data
- **Recommendations**: Suggests improvements based on patterns
- **Comparisons**: Compares different time periods
- **Insights**: Provides data-driven observations

## 📊 Statistics & Analytics

### Available Charts:
- **Stress Level Trends**: Line chart showing stress over time
- **Financial Overview**: Income vs expenses bar chart
- **Mood Distribution**: Pie chart of mood categories
- **Productivity Metrics**: Focus time and task completion

### Key Metrics:
- Total entries tracked
- Current streak (consecutive days)
- Net financial balance
- Average stress levels

## 🏆 Achievement System

### Achievement Categories:
- **Entry Milestones**: First entry, streak achievements
- **Data Quality**: Consistent tracking, complete entries
- **Goal Progress**: Meeting personal objectives
- **Engagement**: AI chat usage, search frequency

### Progress Tracking:
- Visual progress bars for each achievement
- Unlock dates for completed achievements
- Percentage completion overview

## ⚙️ Settings & Customization

### Accessibility Options:
- **Plain Mode**: Text-only interface for screen readers
- **High Contrast**: Enhanced visibility mode
- **Large Text**: Bigger font sizes

### Display Preferences:
- **Theme Selection**: Terminal, dark, light, high contrast
- **Animations**: Enable/disable smooth transitions
- **Sound Effects**: Audio feedback for actions

### Data Formats:
- **Date Format**: YYYY-MM-DD, MM/DD/YYYY, DD/MM/YYYY
- **Time Format**: 24-hour or 12-hour clock

## 👤 Profile Management

### Profile Sections:
1. **Basic Info**: Name, email, age, occupation
2. **Emotional Profile**: Stress triggers, coping strategies
3. **Work Profile**: Environment, hours, satisfaction
4. **Financial Profile**: Income range, goals, habits
5. **Personal Goals**: Short-term and long-term objectives
6. **AI Preferences**: Response tone, context depth

### AI Tone Options:
- **Supportive**: Encouraging and empathetic
- **Professional**: Direct and business-focused
- **Casual**: Friendly and conversational
- **Direct**: Straightforward and concise

## 🎨 Terminal Interface Features

### Authentic Terminal Experience:
- Monospace typography (Roboto Mono)
- Cyan accent colors for borders and highlights
- Panel-based layout with consistent styling
- Numbered menu navigation system
- Status bars and progress indicators

### Color Coding:
- **Green**: Positive values, success, unlocked achievements
- **Red**: Negative values, errors, high stress
- **Yellow**: Warnings, medium stress, progress
- **Cyan**: Primary UI elements, borders, accents

## 🔧 Troubleshooting

### Common Issues:
- **App won't start**: Check Flutter installation and dependencies
- **Data not saving**: Verify storage permissions
- **Charts not loading**: Ensure fl_chart dependency is installed
- **AI chat not responding**: Check internet connection

### Performance Tips:
- Clear cache regularly in Settings > Advanced
- Limit search results for better performance
- Use date ranges to filter large datasets
- Enable animations only on capable devices

## 📞 Support

### Getting Help:
- Use the **Help** menu (press **h**) for quick reference
- Check **Settings** > **About** for version information
- Visit our GitHub repository for detailed documentation
- Report issues at: https://github.com/your-repo/tracker-terminal

### Feedback:
We welcome your feedback! Use the **Settings** > **Feedback** option to share your thoughts and suggestions.

---

**Remember**: Consistent tracking leads to better insights. The more data you enter, the more meaningful the AI analysis and statistics will be!
""";

    return Scaffold(
      backgroundColor: TerminalTheme.backgroundBlack,
      appBar: AppBar(
        title: Text(
          '❓ Help',
          style: TerminalTheme.terminalHeader,
        ),
        backgroundColor: TerminalTheme.backgroundDark,
        elevation: 0,
      ),
      body: Column(
        children: [
          // Quick command reference
          Container(
            padding: const EdgeInsets.all(16),
            color: TerminalTheme.backgroundDark,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                _buildQuickCommand('1-9', 'Main Menu'),
                _buildQuickCommand('h', 'Help'),
                _buildQuickCommand('0', 'About'),
                _buildQuickCommand('←', 'Back'),
              ],
            ),
          ),
          
          // Help content
          Expanded(
            child: TerminalPanel(
              child: Markdown(
                data: helpContent,
                styleSheet: MarkdownStyleSheet(
                  h1: TerminalTheme.terminalHeader.copyWith(fontSize: 20),
                  h2: TerminalTheme.terminalHeader.copyWith(fontSize: 18),
                  h3: TerminalTheme.terminalHeader.copyWith(fontSize: 16),
                  p: TerminalTheme.terminalText,
                  strong: TerminalTheme.terminalTextBold,
                  em: TerminalTheme.terminalText.copyWith(fontStyle: FontStyle.italic),
                  code: TerminalTheme.terminalText.copyWith(
                    backgroundColor: TerminalTheme.backgroundDark,
                    fontFamily: 'monospace',
                  ),
                  listBullet: TerminalTheme.terminalText,
                  blockquote: TerminalTheme.terminalText.copyWith(
                    color: TerminalTheme.textDim,
                    fontStyle: FontStyle.italic,
                  ),
                ),
              ),
            ),
          ),
          
          // Bottom action bar
          Container(
            padding: const EdgeInsets.all(16),
            color: TerminalTheme.backgroundDark,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                TextButton(
                  onPressed: () => _showCommandReference(),
                  child: Text(
                    'Command Reference',
                    style: TerminalTheme.terminalText.copyWith(
                      color: TerminalTheme.primaryCyan,
                    ),
                  ),
                ),
                TextButton(
                  onPressed: () => _showKeyboardShortcuts(),
                  child: Text(
                    'Keyboard Shortcuts',
                    style: TerminalTheme.terminalText.copyWith(
                      color: TerminalTheme.primaryCyan,
                    ),
                  ),
                ),
                TextButton(
                  onPressed: () => _showContactInfo(),
                  child: Text(
                    'Contact Support',
                    style: TerminalTheme.terminalText.copyWith(
                      color: TerminalTheme.primaryCyan,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickCommand(String key, String description) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          decoration: BoxDecoration(
            color: TerminalTheme.backgroundBlack,
            border: Border.all(color: TerminalTheme.primaryCyan),
            borderRadius: BorderRadius.circular(0),
          ),
          child: Text(
            key,
            style: TerminalTheme.terminalTextBold.copyWith(
              color: TerminalTheme.primaryCyan,
            ),
          ),
        ),
        const SizedBox(height: 4),
        Text(
          description,
          style: TerminalTheme.terminalTextDim.copyWith(fontSize: 10),
        ),
      ],
    );
  }

  void _showCommandReference() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: TerminalTheme.backgroundDark,
        title: Text(
          'Command Reference',
          style: TerminalTheme.terminalHeader,
        ),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              _buildCommandItem('1', 'New Entry', 'Create a new tracker entry'),
              _buildCommandItem('2', 'View Entries', 'Browse recent entries'),
              _buildCommandItem('3', 'Search', 'Search by date or text'),
              _buildCommandItem('4', 'AI Chat', 'Chat with AI assistant'),
              _buildCommandItem('5', 'Statistics', 'View analytics and charts'),
              _buildCommandItem('6', 'Profile', 'Manage your profile'),
              _buildCommandItem('7', 'Export', 'Export your data'),
              _buildCommandItem('8', 'Achievements', 'View achievements'),
              _buildCommandItem('9', 'Settings', 'App preferences'),
              _buildCommandItem('h', 'Help', 'Show this help'),
              _buildCommandItem('0', 'About', 'App information'),
            ],
          ),
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

  Widget _buildCommandItem(String command, String title, String description) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 32,
            height: 32,
            decoration: BoxDecoration(
              color: TerminalTheme.primaryCyan.withOpacity(0.2),
              border: Border.all(color: TerminalTheme.primaryCyan),
            ),
            child: Center(
              child: Text(
                command,
                style: TerminalTheme.terminalTextBold.copyWith(
                  color: TerminalTheme.primaryCyan,
                ),
              ),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: TerminalTheme.terminalTextBold,
                ),
                const SizedBox(height: 2),
                Text(
                  description,
                  style: TerminalTheme.terminalTextDim.copyWith(fontSize: 12),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  void _showKeyboardShortcuts() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: TerminalTheme.backgroundDark,
        title: Text(
          'Keyboard Shortcuts',
          style: TerminalTheme.terminalHeader,
        ),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              _buildShortcutItem('Number Keys (1-9)', 'Navigate to menu items'),
              _buildShortcutItem('h / H', 'Open help screen'),
              _buildShortcutItem('0', 'Open about screen'),
              _buildShortcutItem('Backspace', 'Go back / close dialog'),
              _buildShortcutItem('Enter', 'Submit form / confirm action'),
              _buildShortcutItem('Tab', 'Move between form fields'),
              _buildShortcutItem('Escape', 'Cancel current operation'),
            ],
          ),
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

  Widget _buildShortcutItem(String shortcut, String description) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: TerminalTheme.backgroundBlack,
              border: Border.all(color: TerminalTheme.borderGray),
            ),
            child: Text(
              shortcut,
              style: TerminalTheme.terminalTextBold,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              description,
              style: TerminalTheme.terminalText,
            ),
          ),
        ],
      ),
    );
  }

  void _showContactInfo() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: TerminalTheme.backgroundDark,
        title: Text(
          'Contact Support',
          style: TerminalTheme.terminalHeader,
        ),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                'Need help or have feedback?',
                style: TerminalTheme.terminalTextBold,
              ),
              const SizedBox(height: 16),
              _buildContactItem('📧', 'Email', 'support@tracker-terminal.com'),
              const SizedBox(height: 8),
              _buildContactItem('🐛', 'Issues', 'github.com/your-repo/tracker-terminal'),
              const SizedBox(height: 8),
              _buildContactItem('💬', 'Discord', 'discord.gg/tracker-terminal'),
              const SizedBox(height: 16),
              Text(
                'When reporting issues, please include:',
                style: TerminalTheme.terminalTextBold,
              ),
              const SizedBox(height: 8),
              Text(
                '• App version\n• Device information\n• Steps to reproduce\n• Screenshots if applicable',
                style: TerminalTheme.terminalText.copyWith(fontSize: 12),
              ),
            ],
          ),
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

  Widget _buildContactItem(String icon, String type, String value) {
    return Row(
      children: [
        Text(
          icon,
          style: const TextStyle(fontSize: 16),
        ),
        const SizedBox(width: 8),
        Text(
          '$type: ',
          style: TerminalTheme.terminalTextBold,
        ),
        Expanded(
          child: Text(
            value,
            style: TerminalTheme.terminalText.copyWith(
              color: TerminalTheme.primaryCyan,
            ),
          ),
        ),
      ],
    );
  }
}