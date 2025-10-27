import 'package:flutter/material.dart';
import '../theme/terminal_theme.dart';
import '../widgets/terminal_panel.dart';
import '../widgets/terminal_table.dart';

class EntriesScreen extends StatelessWidget {
  const EntriesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    // Sample data - in a real app, this would come from your API
    final sampleEntries = [
      ['2024-01-15', '\$50.00', '7', 'Great day at work', 'Good'],
      ['2024-01-14', '-\$25.50', '4', 'Average day', 'Neutral'],
      ['2024-01-13', '\$100.00', '2', 'Productive meeting', 'Excellent'],
      ['2024-01-12', '\$0.00', '8', 'Stressful deadline', 'Poor'],
      ['2024-01-11', '\$75.25', '3', 'Good progress', 'Good'],
    ];

    final rowColors = sampleEntries.map((entry) {
      final stressLevel = int.parse(entry[2]);
      return TerminalTheme.getStressColor(stressLevel);
    }).toList();

    return Scaffold(
      backgroundColor: TerminalTheme.backgroundBlack,
      appBar: AppBar(
        title: Text(
          '📋 Recent Entries',
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
            // Header
            Text(
              'Last 30 Days',
              style: TerminalTheme.terminalHeader.copyWith(fontSize: 16),
            ),
            const SizedBox(height: 8),
            Text(
              '${sampleEntries.length} entries found',
              style: TerminalTheme.terminalTextDim,
            ),
            const SizedBox(height: 16),
            
            // Entries table
            Expanded(
              child: TerminalPanel(
                child: TerminalTable(
                  headers: ['Date', 'Finance', 'Stress', 'Work Notes', 'Mood'],
                  rows: sampleEntries,
                  rowColors: rowColors,
                ),
              ),
            ),
            
            const SizedBox(height: 16),
            
            // Action buttons
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                ElevatedButton(
                  onPressed: () => Navigator.pushNamed(context, '/new-entry'),
                  child: const Text('New Entry'),
                ),
                TextButton(
                  onPressed: () => Navigator.pushNamed(context, '/search'),
                  child: Text(
                    'Search',
                    style: TerminalTheme.terminalText.copyWith(
                      color: TerminalTheme.primaryCyan,
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}