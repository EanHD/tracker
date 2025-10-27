import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import '../theme/terminal_theme.dart';
import '../widgets/terminal_panel.dart';

class AboutScreen extends StatelessWidget {
  const AboutScreen({super.key});

  @override
  Widget build(BuildContext context) {
    const aboutContent = """
# Tracker Terminal

**Version 1.0.0** • **Build 2024.01.15**

A comprehensive personal tracking application that brings the power and aesthetic of terminal interfaces to mobile devices. Track your daily activities, mood, finances, and productivity with an authentic command-line experience.

## 🎯 Mission

To provide users with a powerful, privacy-focused tracking tool that combines the efficiency of terminal interfaces with modern mobile capabilities, enabling better self-awareness and personal growth through data-driven insights.

## ✨ Key Features

### **Authentic Terminal Experience**
- Monospace typography and cyan color scheme
- Numbered menu navigation system
- Panel-based interface design
- Command-line aesthetic throughout

### **Comprehensive Tracking**
- **Finance**: Income, expenses, budget monitoring
- **Wellbeing**: Stress levels, mood tracking, health metrics
- **Work**: Productivity, accomplishments, time management
- **Personal**: Journal entries, reflections, goal tracking

### **AI-Powered Insights**
- Intelligent chat assistant for data analysis
- Pattern recognition and trend identification
- Personalized recommendations
- Natural language queries

### **Advanced Analytics**
- Interactive charts and visualizations
- Statistical analysis and trend reporting
- Achievement system with progress tracking
- Export capabilities for data portability

## 🛠️ Technical Details

### **Architecture**
- **Frontend**: Flutter framework for cross-platform compatibility
- **Backend**: Python FastAPI with SQLAlchemy ORM
- **Database**: SQLite for local data storage
- **AI Integration**: Custom language model for insights

### **Dependencies**
- **UI Components**: flutter_markdown, google_fonts, fl_chart
- **State Management**: provider, shared_preferences
- **Data Processing**: intl for date/time formatting
- **HTTP Client**: http for API communication

### **Platform Support**
- **Mobile**: iOS and Android
- **Desktop**: Windows, macOS, Linux (future)
- **Web**: Progressive Web App (future)

## 🔒 Privacy & Security

### **Data Protection**
- All data stored locally on your device
- No external servers for personal data
- Optional cloud sync with end-to-end encryption
- Complete control over data sharing

### **Transparency**
- Open source codebase
- Clear privacy policy
- No hidden data collection
- User-controlled data export/deletion

## 🚀 Development Roadmap

### **Version 1.1 (Coming Soon)**
- Enhanced AI chat with context awareness
- Advanced statistical analysis features
- Custom achievement creation
- Data import from other apps

### **Version 2.0 (Future)**
- Multi-device synchronization
- Advanced machine learning insights
- Community features and sharing
- Plugin system for extensions

### **Long-term Vision**
- Wearable device integration
- Advanced predictive analytics
- Community-driven features
- Enterprise team tracking

## 👥 Team & Contributors

### **Core Development Team**
- **Lead Developer**: Terminal UI/UX specialist
- **Backend Engineer**: API and database architecture
- **AI/ML Engineer**: Intelligence and insights system
- **Mobile Developer**: Flutter and cross-platform optimization

### **Open Source Contributors**
This project welcomes contributions from the community. Special thanks to all contributors who have helped improve the app.

## 📄 License

**MIT License**

Copyright (c) 2024 Tracker Terminal Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

## 🙏 Acknowledgments

- **Flutter Community**: For excellent documentation and packages
- **Terminal Design Philosophy**: Inspired by classic CLI applications
- **Open Source Contributors**: For libraries and tools that made this possible
- **Beta Testers**: For valuable feedback and testing

## 📱 App Information

- **Package Name**: com.tracker.terminal
- **Minimum SDK**: Flutter 3.0+
- **Target Platforms**: iOS 12+, Android 6.0+
- **App Size**: ~25MB (varies by platform)
- **Languages**: English (more coming soon)

---

**Tracker Terminal** - *"Track your life, terminal style."*

*Built with ❤️ for the command-line enthusiasts who appreciate both power and simplicity.*
""";

    return Scaffold(
      backgroundColor: TerminalTheme.backgroundBlack,
      appBar: AppBar(
        title: Text(
          'ℹ️ About',
          style: TerminalTheme.terminalHeader,
        ),
        backgroundColor: TerminalTheme.backgroundDark,
        elevation: 0,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // App header
            Center(
              child: Column(
                children: [
                  Text(
                    '📊 Tracker Terminal',
                    style: TerminalTheme.terminalHeader.copyWith(fontSize: 24),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Version 1.0.0 • Build 2024.01.15',
                    style: TerminalTheme.terminalTextDim,
                  ),
                  const SizedBox(height: 16),
                  Container(
                    width: 80,
                    height: 80,
                    decoration: BoxDecoration(
                      color: TerminalTheme.primaryCyan.withOpacity(0.2),
                      border: Border.all(color: TerminalTheme.primaryCyan, width: 2),
                      borderRadius: BorderRadius.circular(0),
                    ),
                    child: const Center(
                      child: Text(
                        'TT',
                        style: TextStyle(
                          fontSize: 32,
                          fontWeight: FontWeight.bold,
                          color: TerminalTheme.primaryCyan,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),
            
            // Main content
            TerminalPanel(
              child: Markdown(
                data: aboutContent,
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
            
            const SizedBox(height: 24),
            
            // Action buttons
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                ElevatedButton(
                  onPressed: () => _showLicenseDialog(),
                  child: const Text('View License'),
                ),
                TextButton(
                  onPressed: () => _showPrivacyPolicy(),
                  child: Text(
                    'Privacy Policy',
                    style: TerminalTheme.terminalText.copyWith(
                      color: TerminalTheme.primaryCyan,
                    ),
                  ),
                ),
                TextButton(
                  onPressed: () => _showTermsOfService(),
                  child: Text(
                    'Terms of Service',
                    style: TerminalTheme.terminalText.copyWith(
                      color: TerminalTheme.primaryCyan,
                    ),
                  ),
                ),
              ],
            ),
            
            const SizedBox(height: 16),
            
            // Version info and credits
            Center(
              child: Column(
                children: [
                  Text(
                    'Made with ❤️ for terminal enthusiasts',
                    style: TerminalTheme.terminalTextDim.copyWith(fontSize: 12),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '© 2024 Tracker Terminal Team',
                    style: TerminalTheme.terminalTextDim.copyWith(fontSize: 10),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showLicenseDialog() {
    const licenseText = """
MIT License

Copyright (c) 2024 Tracker Terminal Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
""";

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: TerminalTheme.backgroundDark,
        title: Text(
          'MIT License',
          style: TerminalTheme.terminalHeader,
        ),
        content: SingleChildScrollView(
          child: Text(
            licenseText,
            style: TerminalTheme.terminalText.copyWith(fontSize: 12),
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

  void _showPrivacyPolicy() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: TerminalTheme.backgroundDark,
        title: Text(
          'Privacy Policy',
          style: TerminalTheme.terminalHeader,
        ),
        content: SingleChildScrollView(
          child: Text(
            'Privacy Policy:\n\n• All data is stored locally on your device\n• No personal information is sent to external servers\n• You control all data sharing and export\n• Data can be deleted at any time\n• No tracking or analytics without consent\n\nWe are committed to protecting your privacy and giving you complete control over your personal data.',
            style: TerminalTheme.terminalText.copyWith(fontSize: 12),
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

  void _showTermsOfService() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: TerminalTheme.backgroundDark,
        title: Text(
          'Terms of Service',
          style: TerminalTheme.terminalHeader,
        ),
        content: SingleChildScrollView(
          child: Text(
            'Terms of Service:\n\n• Use at your own risk\n• Data backup is your responsibility\n• Features may change without notice\n• No warranty is provided\n• Respect others\' privacy when sharing\n\nBy using this app, you agree to these terms and acknowledge that tracking personal data is your responsibility.',
            style: TerminalTheme.terminalText.copyWith(fontSize: 12),
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
}