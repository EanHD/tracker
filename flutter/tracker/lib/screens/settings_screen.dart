import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../theme/terminal_theme.dart';
import '../widgets/terminal_panel.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  bool _plainMode = false;
  bool _highContrast = false;
  bool _animationsEnabled = true;
  bool _soundEffects = false;
  String _dateFormat = 'YYYY-MM-DD';
  String _timeFormat = '24h';
  String _theme = 'terminal';
  
  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _plainMode = prefs.getBool('plain_mode') ?? false;
      _highContrast = prefs.getBool('high_contrast') ?? false;
      _animationsEnabled = prefs.getBool('animations_enabled') ?? true;
      _soundEffects = prefs.getBool('sound_effects') ?? false;
      _dateFormat = prefs.getString('date_format') ?? 'YYYY-MM-DD';
      _timeFormat = prefs.getString('time_format') ?? '24h';
      _theme = prefs.getString('theme') ?? 'terminal';
    });
  }

  Future<void> _saveSetting(String key, dynamic value) async {
    final prefs = await SharedPreferences.getInstance();
    if (value is bool) {
      await prefs.setBool(key, value);
    } else if (value is String) {
      await prefs.setString(key, value);
    }
  }

  void _resetToDefaults() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: TerminalTheme.backgroundDark,
        title: Text(
          'Reset Settings',
          style: TerminalTheme.terminalHeader,
        ),
        content: Text(
          'Are you sure you want to reset all settings to their default values?',
          style: TerminalTheme.terminalText,
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(
              'Cancel',
              style: TerminalTheme.terminalText.copyWith(
                color: TerminalTheme.textWhite,
              ),
            ),
          ),
          ElevatedButton(
            onPressed: () {
              setState(() {
                _plainMode = false;
                _highContrast = false;
                _animationsEnabled = true;
                _soundEffects = false;
                _dateFormat = 'YYYY-MM-DD';
                _timeFormat = '24h';
                _theme = 'terminal';
              });
              _saveAllSettings();
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text(
                    'Settings reset to defaults',
                    style: TerminalTheme.terminalText,
                  ),
                  backgroundColor: TerminalTheme.warningYellow,
                ),
              );
            },
            child: const Text('Reset All'),
          ),
        ],
      ),
    );
  }

  Future<void> _saveAllSettings() async {
    await _saveSetting('plain_mode', _plainMode);
    await _saveSetting('high_contrast', _highContrast);
    await _saveSetting('animations_enabled', _animationsEnabled);
    await _saveSetting('sound_effects', _soundEffects);
    await _saveSetting('date_format', _dateFormat);
    await _saveSetting('time_format', _timeFormat);
    await _saveSetting('theme', _theme);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: TerminalTheme.backgroundBlack,
      appBar: AppBar(
        title: Text(
          '⚙️ Settings',
          style: TerminalTheme.terminalHeader,
        ),
        backgroundColor: TerminalTheme.backgroundDark,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.restore),
            onPressed: _resetToDefaults,
            tooltip: 'Reset to defaults',
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Accessibility Settings
            Text(
              'Accessibility',
              style: TerminalTheme.terminalHeader.copyWith(fontSize: 16),
            ),
            const SizedBox(height: 16),
            TerminalPanel(
              child: Column(
                children: [
                  _buildSettingsSwitch(
                    'Plain Mode (Text-only)',
                    'Enable for screen reader compatibility',
                    _plainMode,
                    (value) {
                      setState(() {
                        _plainMode = value;
                        _saveSetting('plain_mode', value);
                      });
                    },
                  ),
                  const Divider(color: TerminalTheme.borderGray),
                  _buildSettingsSwitch(
                    'High Contrast',
                    'Increase contrast for better visibility',
                    _highContrast,
                    (value) {
                      setState(() {
                        _highContrast = value;
                        _saveSetting('high_contrast', value);
                      });
                    },
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),
            
            // Display Settings
            Text(
              'Display & Interface',
              style: TerminalTheme.terminalHeader.copyWith(fontSize: 16),
            ),
            const SizedBox(height: 16),
            TerminalPanel(
              child: Column(
                children: [
                  _buildSettingsSwitch(
                    'Animations',
                    'Enable smooth transitions and animations',
                    _animationsEnabled,
                    (value) {
                      setState(() {
                        _animationsEnabled = value;
                        _saveSetting('animations_enabled', value);
                      });
                    },
                  ),
                  const Divider(color: TerminalTheme.borderGray),
                  _buildSettingsSwitch(
                    'Sound Effects',
                    'Play sounds for notifications and actions',
                    _soundEffects,
                    (value) {
                      setState(() {
                        _soundEffects = value;
                        _saveSetting('sound_effects', value);
                      });
                    },
                  ),
                  const Divider(color: TerminalTheme.borderGray),
                  _buildDropdownSetting(
                    'Theme',
                    'Application visual theme',
                    _theme,
                    ['terminal', 'dark', 'light', 'high contrast'],
                    (value) {
                      setState(() {
                        _theme = value!;
                        _saveSetting('theme', value);
                      });
                    },
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),
            
            // Data & Format Settings
            Text(
              'Data & Formats',
              style: TerminalTheme.terminalHeader.copyWith(fontSize: 16),
            ),
            const SizedBox(height: 16),
            TerminalPanel(
              child: Column(
                children: [
                  _buildDropdownSetting(
                    'Date Format',
                    'How dates are displayed',
                    _dateFormat,
                    ['YYYY-MM-DD', 'MM/DD/YYYY', 'DD/MM/YYYY'],
                    (value) {
                      setState(() {
                        _dateFormat = value!;
                        _saveSetting('date_format', value);
                      });
                    },
                  ),
                  const Divider(color: TerminalTheme.borderGray),
                  _buildDropdownSetting(
                    'Time Format',
                    '12-hour or 24-hour time',
                    _timeFormat,
                    ['24h', '12h'],
                    (value) {
                      setState(() {
                        _timeFormat = value!;
                        _saveSetting('time_format', value);
                      });
                    },
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),
            
            // Advanced Settings
            Text(
              'Advanced',
              style: TerminalTheme.terminalHeader.copyWith(fontSize: 16),
            ),
            const SizedBox(height: 16),
            TerminalPanel(
              child: Column(
                children: [
                  _buildActionButton(
                    'Clear Cache',
                    'Remove temporary data and images',
                    () => _showClearCacheDialog(),
                  ),
                  const Divider(color: TerminalTheme.borderGray),
                  _buildActionButton(
                    'Export Settings',
                    'Save settings to file',
                    () => _exportSettings(),
                  ),
                  const Divider(color: TerminalTheme.borderGray),
                  _buildActionButton(
                    'Import Settings',
                    'Load settings from file',
                    () => _importSettings(),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),
            
            // App Information
            Text(
              'Application',
              style: TerminalTheme.terminalHeader.copyWith(fontSize: 16),
            ),
            const SizedBox(height: 16),
            TerminalPanel(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildInfoRow('Version', '1.0.0'),
                  const Divider(color: TerminalTheme.borderGray),
                  _buildInfoRow('Build', '2024.01.15'),
                  const Divider(color: TerminalTheme.borderGray),
                  _buildInfoRow('Database', 'SQLite'),
                  const Divider(color: TerminalTheme.borderGray),
                  _buildInfoRow('Last Backup', 'Never'),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSettingsSwitch(String title, String description, bool value, ValueChanged<bool> onChanged) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: TerminalTheme.terminalText,
                ),
                const SizedBox(height: 2),
                Text(
                  description,
                  style: TerminalTheme.terminalTextDim.copyWith(fontSize: 12),
                ),
              ],
            ),
          ),
          Switch(
            value: value,
            onChanged: onChanged,
            activeColor: TerminalTheme.primaryCyan,
          ),
        ],
      ),
    );
  }

  Widget _buildDropdownSetting(String title, String description, String currentValue, 
      List<String> options, ValueChanged<String?> onChanged) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: TerminalTheme.terminalText,
          ),
          const SizedBox(height: 2),
          Text(
            description,
            style: TerminalTheme.terminalTextDim.copyWith(fontSize: 12),
          ),
          const SizedBox(height: 8),
          Container(
            decoration: BoxDecoration(
              border: Border.all(color: TerminalTheme.borderGray),
              color: TerminalTheme.backgroundDark,
            ),
            child: DropdownButton<String>(
              value: currentValue,
              dropdownColor: TerminalTheme.backgroundDark,
              isExpanded: true,
              underline: const SizedBox(),
              style: TerminalTheme.terminalText,
              items: options.map((String value) {
                return DropdownMenuItem<String>(
                  value: value,
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 12),
                    child: Text(value),
                  ),
                );
              }).toList(),
              onChanged: onChanged,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildActionButton(String title, String description, VoidCallback onPressed) {
    return InkWell(
      onTap: onPressed,
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 8),
        child: Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: TerminalTheme.terminalText,
                  ),
                  const SizedBox(height: 2),
                  Text(
                    description,
                    style: TerminalTheme.terminalTextDim.copyWith(fontSize: 12),
                  ),
                ],
              ),
            ),
            const Icon(
              Icons.chevron_right,
              color: TerminalTheme.primaryCyan,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: TerminalTheme.terminalText,
          ),
          Text(
            value,
            style: TerminalTheme.terminalTextDim,
          ),
        ],
      ),
    );
  }

  void _showClearCacheDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: TerminalTheme.backgroundDark,
        title: Text(
          'Clear Cache',
          style: TerminalTheme.terminalHeader,
        ),
        content: Text(
          'This will remove all cached images and temporary data. Continue?',
          style: TerminalTheme.terminalText,
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(
              'Cancel',
              style: TerminalTheme.terminalText.copyWith(
                color: TerminalTheme.textWhite,
              ),
            ),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text(
                    'Cache cleared successfully',
                    style: TerminalTheme.terminalText,
                  ),
                  backgroundColor: TerminalTheme.successGreen,
                ),
              );
            },
            child: const Text('Clear'),
          ),
        ],
      ),
    );
  }

  void _exportSettings() {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          'Settings export feature coming soon!',
          style: TerminalTheme.terminalText,
        ),
        backgroundColor: TerminalTheme.warningYellow,
      ),
    );
  }

  void _importSettings() {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          'Settings import feature coming soon!',
          style: TerminalTheme.terminalText,
        ),
        backgroundColor: TerminalTheme.warningYellow,
      ),
    );
  }
}