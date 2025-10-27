import 'package:flutter/material.dart';
import '../theme/terminal_theme.dart';
import '../widgets/terminal_panel.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  int _currentStep = 0;
  
  // Profile data
  final _nameController = TextEditingController(text: 'John Doe');
  final _emailController = TextEditingController(text: 'john@example.com');
  final _ageController = TextEditingController(text: '28');
  final _occupationController = TextEditingController(text: 'Software Developer');
  
  // Emotional profile
  String _stressTrigger = 'Work deadlines';
  String _copingStrategy = 'Exercise and meditation';
  String _supportSystem = 'Family and close friends';
  
  // Work profile
  String _workEnvironment = 'Remote';
  String _workHours = '9-5';
  String _jobSatisfaction = 'Satisfied';
  
  // Financial profile
  String _incomeRange = '50k-75k';
  String _savingsGoal = 'Emergency fund';
  String _spendingHabit = 'Moderate';
  
  // Goals
  final _shortTermGoalsController = TextEditingController(text: 'Improve work-life balance, exercise 3x per week');
  final _longTermGoalsController = TextEditingController(text: 'Financial independence, start own business');
  
  // Preferences
  String _aiTone = 'Supportive';
  String _contextDepth = 'Detailed';
  bool _plainMode = false;

  final List<String> _steps = [
    'Basic Info',
    'Emotional Profile',
    'Work Profile',
    'Financial Profile',
    'Goals',
    'Preferences'
  ];

  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    _ageController.dispose();
    _occupationController.dispose();
    _shortTermGoalsController.dispose();
    _longTermGoalsController.dispose();
    super.dispose();
  }

  void _nextStep() {
    if (_currentStep < _steps.length - 1) {
      setState(() {
        _currentStep++;
      });
    }
  }

  void _previousStep() {
    if (_currentStep > 0) {
      setState(() {
        _currentStep--;
      });
    }
  }

  void _saveProfile() {
    // Simulate saving profile
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          'Profile updated successfully!',
          style: TerminalTheme.terminalText,
        ),
        backgroundColor: TerminalTheme.successGreen,
      ),
    );
    Navigator.pop(context);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: TerminalTheme.backgroundBlack,
      appBar: AppBar(
        title: Text(
          '👤 Profile Management',
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
            // Progress indicator
            Text(
              'Step ${_currentStep + 1} of ${_steps.length}',
              style: TerminalTheme.terminalTextDim,
            ),
            const SizedBox(height: 8),
            LinearProgressIndicator(
              value: (_currentStep + 1) / _steps.length,
              backgroundColor: TerminalTheme.borderGray,
              valueColor: const AlwaysStoppedAnimation<Color>(TerminalTheme.primaryCyan),
            ),
            const SizedBox(height: 16),
            
            // Current step title
            Text(
              _steps[_currentStep],
              style: TerminalTheme.terminalHeader.copyWith(fontSize: 20),
            ),
            const SizedBox(height: 16),
            
            // Current step content
            Expanded(
              child: TerminalPanel(
                child: _buildCurrentStepContent(),
              ),
            ),
            
            const SizedBox(height: 16),
            
            // Navigation buttons
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                if (_currentStep > 0)
                  TextButton(
                    onPressed: _previousStep,
                    child: Text(
                      '< Previous',
                      style: TerminalTheme.terminalText.copyWith(
                        color: TerminalTheme.primaryCyan,
                      ),
                    ),
                  )
                else
                  const SizedBox(width: 80),
                
                if (_currentStep < _steps.length - 1)
                  ElevatedButton(
                    onPressed: _nextStep,
                    child: const Text('Next >'),
                  )
                else
                  ElevatedButton(
                    onPressed: _saveProfile,
                    child: const Text('Save Profile'),
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCurrentStepContent() {
    switch (_currentStep) {
      case 0:
        return _buildBasicInfoStep();
      case 1:
        return _buildEmotionalProfileStep();
      case 2:
        return _buildWorkProfileStep();
      case 3:
        return _buildFinancialProfileStep();
      case 4:
        return _buildGoalsStep();
      case 5:
        return _buildPreferencesStep();
      default:
        return const SizedBox();
    }
  }

  Widget _buildBasicInfoStep() {
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Basic Information',
            style: TerminalTheme.terminalHeader.copyWith(fontSize: 16),
          ),
          const SizedBox(height: 16),
          _buildTextField('Name', _nameController, 'Your full name'),
          const SizedBox(height: 12),
          _buildTextField('Email', _emailController, 'your@email.com'),
          const SizedBox(height: 12),
          _buildTextField('Age', _ageController, '25', keyboardType: TextInputType.number),
          const SizedBox(height: 12),
          _buildTextField('Occupation', _occupationController, 'Your job title'),
        ],
      ),
    );
  }

  Widget _buildEmotionalProfileStep() {
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Emotional Profile',
            style: TerminalTheme.terminalHeader.copyWith(fontSize: 16),
          ),
          const SizedBox(height: 16),
          _buildDropdownField(
            'Primary Stress Trigger',
            _stressTrigger,
            ['Work deadlines', 'Financial pressure', 'Relationship issues', 'Health concerns', 'Time management'],
            (value) => setState(() => _stressTrigger = value!),
          ),
          const SizedBox(height: 12),
          _buildDropdownField(
            'Preferred Coping Strategy',
            _copingStrategy,
            ['Exercise and meditation', 'Talking with friends', 'Creative activities', 'Nature walks', 'Reading'],
            (value) => setState(() => _copingStrategy = value!),
          ),
          const SizedBox(height: 12),
          _buildDropdownField(
            'Support System',
            _supportSystem,
            ['Family and close friends', 'Professional network', 'Online communities', 'Therapist/counselor', 'Self-reliant'],
            (value) => setState(() => _supportSystem = value!),
          ),
        ],
      ),
    );
  }

  Widget _buildWorkProfileStep() {
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Work Profile',
            style: TerminalTheme.terminalHeader.copyWith(fontSize: 16),
          ),
          const SizedBox(height: 16),
          _buildDropdownField(
            'Work Environment',
            _workEnvironment,
            ['Remote', 'Hybrid', 'Office', 'Field work', 'Self-employed'],
            (value) => setState(() => _workEnvironment = value!),
          ),
          const SizedBox(height: 12),
          _buildDropdownField(
            'Typical Work Hours',
            _workHours,
            ['9-5', 'Flexible', 'Shift work', 'Part-time', 'Freelance'],
            (value) => setState(() => _workHours = value!),
          ),
          const SizedBox(height: 12),
          _buildDropdownField(
            'Job Satisfaction',
            _jobSatisfaction,
            ['Very satisfied', 'Satisfied', 'Neutral', 'Dissatisfied', 'Very dissatisfied'],
            (value) => setState(() => _jobSatisfaction = value!),
          ),
        ],
      ),
    );
  }

  Widget _buildFinancialProfileStep() {
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Financial Profile',
            style: TerminalTheme.terminalHeader.copyWith(fontSize: 16),
          ),
          const SizedBox(height: 16),
          _buildDropdownField(
            'Income Range',
            _incomeRange,
            ['< 25k', '25k-50k', '50k-75k', '75k-100k', '100k+'],
            (value) => setState(() => _incomeRange = value!),
          ),
          const SizedBox(height: 12),
          _buildDropdownField(
            'Primary Savings Goal',
            _savingsGoal,
            ['Emergency fund', 'Retirement', 'House purchase', 'Education', 'Travel'],
            (value) => setState(() => _savingsGoal = value!),
          ),
          const SizedBox(height: 12),
          _buildDropdownField(
            'Spending Habit',
            _spendingHabit,
            ['Conservative', 'Moderate', 'Liberal', 'Impulsive', 'Budget-conscious'],
            (value) => setState(() => _spendingHabit = value!),
          ),
        ],
      ),
    );
  }

  Widget _buildGoalsStep() {
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Personal Goals',
            style: TerminalTheme.terminalHeader.copyWith(fontSize: 16),
          ),
          const SizedBox(height: 16),
          _buildTextAreaField(
            'Short-term Goals (3-6 months)',
            _shortTermGoalsController,
            'e.g., Improve work-life balance, exercise 3x per week',
          ),
          const SizedBox(height: 12),
          _buildTextAreaField(
            'Long-term Goals (1-5 years)',
            _longTermGoalsController,
            'e.g., Financial independence, start own business',
          ),
        ],
      ),
    );
  }

  Widget _buildPreferencesStep() {
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'AI Preferences',
            style: TerminalTheme.terminalHeader.copyWith(fontSize: 16),
          ),
          const SizedBox(height: 16),
          _buildDropdownField(
            'AI Response Tone',
            _aiTone,
            ['Supportive', 'Professional', 'Casual', 'Direct', 'Encouraging'],
            (value) => setState(() => _aiTone = value!),
          ),
          const SizedBox(height: 12),
          _buildDropdownField(
            'Context Depth',
            _contextDepth,
            ['Brief', 'Standard', 'Detailed', 'Comprehensive'],
            (value) => setState(() => _contextDepth = value!),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Text(
                'Plain Mode (Text-only)',
                style: TerminalTheme.terminalText,
              ),
              const Spacer(),
              Switch(
                value: _plainMode,
                onChanged: (value) {
                  setState(() {
                    _plainMode = value;
                  });
                },
                activeColor: TerminalTheme.primaryCyan,
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            'Enable plain mode for accessibility or screen reader compatibility',
            style: TerminalTheme.terminalTextDim.copyWith(fontSize: 12),
          ),
        ],
      ),
    );
  }

  Widget _buildTextField(String label, TextEditingController controller, String hint, 
      {TextInputType keyboardType = TextInputType.text}) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: TerminalTheme.terminalText,
        ),
        const SizedBox(height: 4),
        TextField(
          controller: controller,
          style: TerminalTheme.terminalText,
          keyboardType: keyboardType,
          decoration: InputDecoration(
            hintText: hint,
            hintStyle: TerminalTheme.terminalTextDim,
            border: const OutlineInputBorder(),
            enabledBorder: OutlineInputBorder(
              borderSide: BorderSide(color: TerminalTheme.borderGray),
            ),
            focusedBorder: OutlineInputBorder(
              borderSide: BorderSide(color: TerminalTheme.primaryCyan),
            ),
            contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          ),
        ),
      ],
    );
  }

  Widget _buildTextAreaField(String label, TextEditingController controller, String hint) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: TerminalTheme.terminalText,
        ),
        const SizedBox(height: 4),
        TextField(
          controller: controller,
          style: TerminalTheme.terminalText,
          maxLines: 3,
          decoration: InputDecoration(
            hintText: hint,
            hintStyle: TerminalTheme.terminalTextDim,
            border: const OutlineInputBorder(),
            enabledBorder: OutlineInputBorder(
              borderSide: BorderSide(color: TerminalTheme.borderGray),
            ),
            focusedBorder: OutlineInputBorder(
              borderSide: BorderSide(color: TerminalTheme.primaryCyan),
            ),
            contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          ),
        ),
      ],
    );
  }

  Widget _buildDropdownField(String label, String currentValue, List<String> options, 
      ValueChanged<String?> onChanged) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: TerminalTheme.terminalText,
        ),
        const SizedBox(height: 4),
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
    );
  }
}