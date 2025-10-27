import 'package:flutter/material.dart';
import '../theme/terminal_theme.dart';
import '../widgets/terminal_panel.dart';
import '../widgets/terminal_menu_item.dart';

class TerminalHomeScreen extends StatelessWidget {
  const TerminalHomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: TerminalTheme.backgroundBlack,
      appBar: AppBar(
        title: Text(
          '📊 Tracker Terminal',
          style: TerminalTheme.terminalHeader,
        ),
        backgroundColor: TerminalTheme.backgroundDark,
        elevation: 0,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Welcome message
            Text(
              'Welcome to Tracker Terminal',
              style: TerminalTheme.terminalHeader.copyWith(fontSize: 18),
            ),
            const SizedBox(height: 8),
            Text(
              'Select an option:',
              style: TerminalTheme.terminalText,
            ),
            const SizedBox(height: 16),
            
            // Main menu panel
            TerminalPanel(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  TerminalMenuItem(
                    number: '1',
                    icon: '📝',
                    fallbackIcon: '[New]',
                    title: 'New Entry',
                    description: 'Create a new tracker entry',
                    onTap: () => Navigator.pushNamed(context, '/new-entry'),
                  ),
                  const SizedBox(height: 12),
                  TerminalMenuItem(
                    number: '2',
                    icon: '📋',
                    fallbackIcon: '[List]',
                    title: 'View Entries',
                    description: 'Browse your recent entries',
                    onTap: () => Navigator.pushNamed(context, '/entries'),
                  ),
                  const SizedBox(height: 12),
                  TerminalMenuItem(
                    number: '3',
                    icon: '🔍',
                    fallbackIcon: '[Search]',
                    title: 'Search',
                    description: 'Search entries by date or text',
                    onTap: () => Navigator.pushNamed(context, '/search'),
                  ),
                  const SizedBox(height: 12),
                  TerminalMenuItem(
                    number: '4',
                    icon: '💬',
                    fallbackIcon: '[Chat]',
                    title: 'AI Chat',
                    description: 'Chat with AI about your entries',
                    onTap: () => Navigator.pushNamed(context, '/chat'),
                  ),
                  const SizedBox(height: 12),
                  TerminalMenuItem(
                    number: '5',
                    icon: '📈',
                    fallbackIcon: '[Stats]',
                    title: 'Statistics',
                    description: 'View your tracking statistics',
                    onTap: () => Navigator.pushNamed(context, '/stats'),
                  ),
                  const SizedBox(height: 12),
                  TerminalMenuItem(
                    number: '6',
                    icon: '👤',
                    fallbackIcon: '[Profile]',
                    title: 'Profile',
                    description: 'Manage your profile settings',
                    onTap: () => Navigator.pushNamed(context, '/profile'),
                  ),
                  const SizedBox(height: 12),
                  TerminalMenuItem(
                    number: '7',
                    icon: '📤',
                    fallbackIcon: '[Export]',
                    title: 'Export',
                    description: 'Export your data',
                    onTap: () => Navigator.pushNamed(context, '/export'),
                  ),
                  const SizedBox(height: 12),
                  TerminalMenuItem(
                    number: '8',
                    icon: '🏆',
                    fallbackIcon: '[Achieve]',
                    title: 'Achievements',
                    description: 'View your achievements',
                    onTap: () => Navigator.pushNamed(context, '/achievements'),
                  ),
                  const SizedBox(height: 12),
                  TerminalMenuItem(
                    number: '9',
                    icon: '⚙️',
                    fallbackIcon: '[Settings]',
                    title: 'Settings',
                    description: 'Application settings',
                    onTap: () => Navigator.pushNamed(context, '/settings'),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
            
            // Help and exit options
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                TextButton(
                  onPressed: () => Navigator.pushNamed(context, '/help'),
                  child: Text(
                    '[h] Help',
                    style: TerminalTheme.terminalText.copyWith(
                      color: TerminalTheme.primaryCyan,
                    ),
                  ),
                ),
                TextButton(
                  onPressed: () => Navigator.pushNamed(context, '/about'),
                  child: Text(
                    '[0] About',
                    style: TerminalTheme.terminalText.copyWith(
                      color: TerminalTheme.primaryCyan,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            
            // Status bar
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: TerminalTheme.backgroundDark,
                border: Border.all(color: TerminalTheme.borderGray),
              ),
              child: Text(
                'Ready | Press number key or tap option',
                style: TerminalTheme.terminalTextDim,
                textAlign: TextAlign.center,
              ),
            ),
          ],
        ),
      ),
    );
  }
}