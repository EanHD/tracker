import 'package:flutter/material.dart';
import '../theme/terminal_theme.dart';

class TerminalMenuItem extends StatelessWidget {
  final String number;
  final String icon;
  final String fallbackIcon;
  final String title;
  final String description;
  final VoidCallback onTap;
  
  const TerminalMenuItem({
    super.key,
    required this.number,
    required this.icon,
    required this.fallbackIcon,
    required this.title,
    required this.description,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 12),
        decoration: BoxDecoration(
          border: Border(
            bottom: BorderSide(
              color: TerminalTheme.borderGray.withOpacity(0.3),
              width: 0.5,
            ),
          ),
        ),
        child: Row(
          children: [
            // Number key
            Container(
              width: 32,
              height: 32,
              decoration: BoxDecoration(
                color: TerminalTheme.primaryCyan.withOpacity(0.2),
                border: Border.all(color: TerminalTheme.primaryCyan),
                borderRadius: BorderRadius.circular(0),
              ),
              child: Center(
                child: Text(
                  number,
                  style: TerminalTheme.terminalTextBold.copyWith(
                    color: TerminalTheme.primaryCyan,
                  ),
                ),
              ),
            ),
            const SizedBox(width: 16),
            
            // Icon
            Text(
              icon,
              style: const TextStyle(fontSize: 20),
            ),
            const SizedBox(width: 12),
            
            // Content
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
            
            // Arrow indicator
            Text(
              '>',
              style: TerminalTheme.terminalText.copyWith(
                color: TerminalTheme.primaryCyan,
              ),
            ),
          ],
        ),
      ),
    );
  }
}