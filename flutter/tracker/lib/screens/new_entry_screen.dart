import 'package:flutter/material.dart';
import '../theme/terminal_theme.dart';
import '../widgets/terminal_panel.dart';

class NewEntryScreen extends StatefulWidget {
  const NewEntryScreen({super.key});

  @override
  State<NewEntryScreen> createState() => _NewEntryScreenState();
}

class _NewEntryScreenState extends State<NewEntryScreen> {
  final _formKey = GlobalKey<FormState>();
  
  // Form controllers
  final _dateController = TextEditingController();
  final _financeController = TextEditingController();
  final _workNotesController = TextEditingController();
  final _journalController = TextEditingController();
  
  // Form state
  int _stressLevel = 5;
  String _mood = 'Neutral';
  bool _workProductive = false;
  
  final List<String> _moodOptions = ['Excellent', 'Good', 'Neutral', 'Poor'];

  @override
  void dispose() {
    _dateController.dispose();
    _financeController.dispose();
    _workNotesController.dispose();
    _journalController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: TerminalTheme.backgroundBlack,
      appBar: AppBar(
        title: Text(
          '📝 New Entry',
          style: TerminalTheme.terminalHeader,
        ),
        backgroundColor: TerminalTheme.backgroundDark,
        elevation: 0,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Date field
                Text(
                  'Date (YYYY-MM-DD)',
                  style: TerminalTheme.terminalTextBold,
                ),
                const SizedBox(height: 8),
                TextFormField(
                  controller: _dateController,
                  style: TerminalTheme.terminalText,
                  decoration: const InputDecoration(
                    hintText: '2024-01-15',
                  ),
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return 'Please enter a date';
                    }
                    // Simple date validation
                    if (!RegExp(r'^\d{4}-\d{2}-\d{2}$').hasMatch(value)) {
                      return 'Use YYYY-MM-DD format';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 16),
                
                // Finance section
                TerminalPanel(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '💰 Finance',
                        style: TerminalTheme.terminalHeader.copyWith(fontSize: 16),
                      ),
                      const SizedBox(height: 12),
                      Text(
                        'Amount (positive for income, negative for expenses)',
                        style: TerminalTheme.terminalText,
                      ),
                      const SizedBox(height: 8),
                      TextFormField(
                        controller: _financeController,
                        style: TerminalTheme.terminalText,
                        keyboardType: const TextInputType.numberWithOptions(decimal: true),
                        decoration: const InputDecoration(
                          hintText: '0.00',
                          prefixText: '\$ ',
                        ),
                        validator: (value) {
                          if (value == null || value.isEmpty) {
                            return 'Please enter an amount';
                          }
                          if (double.tryParse(value) == null) {
                            return 'Please enter a valid number';
                          }
                          return null;
                        },
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
                
                // Work section
                TerminalPanel(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '💼 Work',
                        style: TerminalTheme.terminalHeader.copyWith(fontSize: 16),
                      ),
                      const SizedBox(height: 12),
                      Text(
                        'Work Notes',
                        style: TerminalTheme.terminalText,
                      ),
                      const SizedBox(height: 8),
                      TextFormField(
                        controller: _workNotesController,
                        style: TerminalTheme.terminalText,
                        maxLines: 3,
                        decoration: const InputDecoration(
                          hintText: 'What did you accomplish today?',
                        ),
                      ),
                      const SizedBox(height: 12),
                      Row(
                        children: [
                          Text(
                            'Productive day?',
                            style: TerminalTheme.terminalText,
                          ),
                          const SizedBox(width: 12),
                          Switch(
                            value: _workProductive,
                            onChanged: (value) {
                              setState(() {
                                _workProductive = value;
                              });
                            },
                            activeColor: TerminalTheme.successGreen,
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
                
                // Wellbeing section
                TerminalPanel(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '🧘 Wellbeing',
                        style: TerminalTheme.terminalHeader.copyWith(fontSize: 16),
                      ),
                      const SizedBox(height: 12),
                      Text(
                        'Stress Level (1-10)',
                        style: TerminalTheme.terminalText,
                      ),
                      const SizedBox(height: 8),
                      Slider(
                        value: _stressLevel.toDouble(),
                        min: 1,
                        max: 10,
                        divisions: 9,
                        activeColor: TerminalTheme.getStressColor(_stressLevel),
                        onChanged: (value) {
                          setState(() {
                            _stressLevel = value.round();
                          });
                        },
                      ),
                      Text(
                        'Level: $_stressLevel',
                        style: TerminalTheme.terminalText.copyWith(
                          color: TerminalTheme.getStressColor(_stressLevel),
                        ),
                      ),
                      const SizedBox(height: 12),
                      Text(
                        'Overall Mood',
                        style: TerminalTheme.terminalText,
                      ),
                      const SizedBox(height: 8),
                      Wrap(
                        spacing: 8,
                        children: _moodOptions.map((mood) {
                          final isSelected = _mood == mood;
                          return ChoiceChip(
                            label: Text(
                              mood,
                              style: TerminalTheme.terminalText.copyWith(
                                color: isSelected 
                                    ? TerminalTheme.backgroundBlack 
                                    : TerminalTheme.textWhite,
                              ),
                            ),
                            selected: isSelected,
                            backgroundColor: TerminalTheme.backgroundDark,
                            selectedColor: TerminalTheme.primaryCyan,
                            onSelected: (selected) {
                              if (selected) {
                                setState(() {
                                  _mood = mood;
                                });
                              }
                            },
                          );
                        }).toList(),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
                
                // Journal section
                TerminalPanel(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '📖 Journal',
                        style: TerminalTheme.terminalHeader.copyWith(fontSize: 16),
                      ),
                      const SizedBox(height: 12),
                      Text(
                        'Personal reflections',
                        style: TerminalTheme.terminalText,
                      ),
                      const SizedBox(height: 8),
                      TextFormField(
                        controller: _journalController,
                        style: TerminalTheme.terminalText,
                        maxLines: 5,
                        decoration: const InputDecoration(
                          hintText: 'Write about your day, thoughts, or feelings...',
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),
                
                // Action buttons
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    ElevatedButton(
                      onPressed: () {
                        if (_formKey.currentState!.validate()) {
                          // TODO: Save entry
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(
                              content: Text(
                                'Entry saved successfully!',
                                style: TerminalTheme.terminalText,
                              ),
                              backgroundColor: TerminalTheme.successGreen,
                            ),
                          );
                          Navigator.pop(context);
                        }
                      },
                      child: const Text('Save Entry'),
                    ),
                    TextButton(
                      onPressed: () => Navigator.pop(context),
                      child: Text(
                        'Cancel',
                        style: TerminalTheme.terminalText.copyWith(
                          color: TerminalTheme.errorRed,
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}