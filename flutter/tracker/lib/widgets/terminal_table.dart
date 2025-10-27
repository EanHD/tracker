import 'package:flutter/material.dart';
import '../theme/terminal_theme.dart';

class TerminalTable extends StatelessWidget {
  final List<String> headers;
  final List<List<String>> rows;
  final List<Color>? rowColors;
  
  const TerminalTable({
    super.key,
    required this.headers,
    required this.rows,
    this.rowColors,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        border: Border.all(color: TerminalTheme.borderGray),
        color: TerminalTheme.backgroundDark,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header row
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: TerminalTheme.backgroundDark,
              border: Border(
                bottom: BorderSide(color: TerminalTheme.primaryCyan),
              ),
            ),
            child: Row(
              children: headers.map((header) {
                return Expanded(
                  child: Text(
                    header,
                    style: TerminalTheme.terminalTextBold.copyWith(
                      color: TerminalTheme.primaryCyan,
                    ),
                  ),
                );
              }).toList(),
            ),
          ),
          
          // Data rows
          ...rows.asMap().entries.map((entry) {
            final index = entry.key;
            final row = entry.value;
            final color = rowColors != null && index < rowColors!.length 
                ? rowColors![index] 
                : TerminalTheme.textWhite;
                
            return Container(
              width: double.infinity,
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                border: Border(
                  bottom: BorderSide(
                    color: TerminalTheme.borderGray.withOpacity(0.3),
                    width: 0.5,
                  ),
                ),
              ),
              child: Row(
                children: row.map((cell) {
                  return Expanded(
                    child: Text(
                      cell,
                      style: TerminalTheme.terminalText.copyWith(color: color),
                    ),
                  );
                }).toList(),
              ),
            );
          }).toList(),
        ],
      ),
    );
  }
}