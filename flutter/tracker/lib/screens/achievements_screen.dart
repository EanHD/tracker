import 'package:flutter/material.dart';
import '../theme/terminal_theme.dart';
import '../widgets/terminal_panel.dart';

class AchievementsScreen extends StatelessWidget {
  const AchievementsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final achievements = [
      Achievement(
        id: 'first_entry',
        title: 'First Steps',
        description: 'Created your first tracker entry',
        icon: '📝',
        isUnlocked: true,
        unlockedDate: DateTime(2024, 1, 15),
        progress: 1,
        target: 1,
      ),
      Achievement(
        id: 'week_streak',
        title: 'Week Warrior',
        description: 'Maintained a 7-day tracking streak',
        icon: '🔥',
        isUnlocked: true,
        unlockedDate: DateTime(2024, 1, 22),
        progress: 7,
        target: 7,
      ),
      Achievement(
        id: 'stress_master',
        title: 'Stress Master',
        description: 'Kept stress levels below 5 for 5 consecutive days',
        icon: '🧘',
        isUnlocked: true,
        unlockedDate: DateTime(2024, 1, 20),
        progress: 5,
        target: 5,
      ),
      Achievement(
        id: 'finance_tracker',
        title: 'Finance Tracker',
        description: 'Tracked financial data for 30 days',
        icon: '💰',
        isUnlocked: false,
        progress: 15,
        target: 30,
      ),
      Achievement(
        id: 'chat_enthusiast',
        title: 'Chat Enthusiast',
        description: 'Had 10 conversations with the AI assistant',
        icon: '💬',
        isUnlocked: false,
        progress: 4,
        target: 10,
      ),
      Achievement(
        id: 'mood_analyst',
        title: 'Mood Analyst',
        description: 'Logged mood data for 14 consecutive days',
        icon: '😊',
        isUnlocked: false,
        progress: 8,
        target: 14,
      ),
      Achievement(
        id: 'productivity_guru',
        title: 'Productivity Guru',
        description: 'Achieved 80% productivity rating for a week',
        icon: '📈',
        isUnlocked: false,
        progress: 3,
        target: 7,
      ),
      Achievement(
        id: 'goal_setter',
        title: 'Goal Setter',
        description: 'Set and tracked progress on 5 personal goals',
        icon: '🎯',
        isUnlocked: false,
        progress: 2,
        target: 5,
      ),
    ];

    final unlockedCount = achievements.where((a) => a.isUnlocked).length;
    final totalCount = achievements.length;
    final completionPercentage = (unlockedCount / totalCount * 100).round();

    return Scaffold(
      backgroundColor: TerminalTheme.backgroundBlack,
      appBar: AppBar(
        title: Text(
          '🏆 Achievements',
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
            // Progress overview
            _buildProgressOverview(unlockedCount, totalCount, completionPercentage),
            const SizedBox(height: 24),
            
            // Achievement categories
            Text(
              'All Achievements',
              style: TerminalTheme.terminalHeader.copyWith(fontSize: 18),
            ),
            const SizedBox(height: 16),
            
            // Achievement list
            Expanded(
              child: ListView.builder(
                itemCount: achievements.length,
                itemBuilder: (context, index) {
                  final achievement = achievements[index];
                  return _buildAchievementCard(achievement);
                },
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildProgressOverview(int unlocked, int total, int percentage) {
    return TerminalPanel(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Progress Overview',
                style: TerminalTheme.terminalHeader.copyWith(fontSize: 16),
              ),
              Text(
                '$unlocked/$total',
                style: TerminalTheme.terminalHeader.copyWith(
                  color: TerminalTheme.primaryCyan,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          LinearProgressIndicator(
            value: unlocked / total,
            backgroundColor: TerminalTheme.borderGray,
            valueColor: const AlwaysStoppedAnimation<Color>(TerminalTheme.primaryCyan),
            minHeight: 8,
          ),
          const SizedBox(height: 8),
          Text(
            '$percentage% Complete',
            style: TerminalTheme.terminalTextDim,
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Container(
                width: 12,
                height: 12,
                color: TerminalTheme.successGreen,
              ),
              const SizedBox(width: 8),
              Text(
                'Unlocked ($unlocked)',
                style: TerminalTheme.terminalText.copyWith(fontSize: 12),
              ),
              const SizedBox(width: 16),
              Container(
                width: 12,
                height: 12,
                color: TerminalTheme.borderGray,
              ),
              const SizedBox(width: 8),
              Text(
                'Locked (${total - unlocked})',
                style: TerminalTheme.terminalText.copyWith(fontSize: 12),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildAchievementCard(Achievement achievement) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      child: TerminalPanel(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                // Achievement icon
                Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    color: achievement.isUnlocked
                        ? TerminalTheme.successGreen.withOpacity(0.2)
                        : TerminalTheme.borderGray.withOpacity(0.2),
                    border: Border.all(
                      color: achievement.isUnlocked
                          ? TerminalTheme.successGreen
                          : TerminalTheme.borderGray,
                    ),
                  ),
                  child: Center(
                    child: Text(
                      achievement.icon,
                      style: const TextStyle(fontSize: 24),
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                
                // Achievement details
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Expanded(
                            child: Text(
                              achievement.title,
                              style: TerminalTheme.terminalTextBold.copyWith(
                                color: achievement.isUnlocked
                                    ? TerminalTheme.textWhite
                                    : TerminalTheme.textDim,
                              ),
                            ),
                          ),
                          if (achievement.isUnlocked)
                            Icon(
                              Icons.check_circle,
                              color: TerminalTheme.successGreen,
                              size: 20,
                            )
                          else
                            Icon(
                              Icons.lock,
                              color: TerminalTheme.textDim,
                              size: 20,
                            ),
                        ],
                      ),
                      const SizedBox(height: 4),
                      Text(
                        achievement.description,
                        style: TerminalTheme.terminalTextDim.copyWith(fontSize: 12),
                      ),
                      if (achievement.isUnlocked && achievement.unlockedDate != null) ...[
                        const SizedBox(height: 4),
                        Text(
                          'Unlocked: ${_formatDate(achievement.unlockedDate!)}',
                          style: TerminalTheme.terminalTextDim.copyWith(fontSize: 10),
                        ),
                      ],
                    ],
                  ),
                ),
              ],
            ),
            
            // Progress bar for locked achievements
            if (!achievement.isUnlocked) ...[
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: LinearProgressIndicator(
                      value: achievement.progress / achievement.target,
                      backgroundColor: TerminalTheme.borderGray,
                      valueColor: AlwaysStoppedAnimation<Color>(
                        achievement.progress / achievement.target >= 0.5
                            ? TerminalTheme.warningYellow
                            : TerminalTheme.primaryCyan,
                      ),
                      minHeight: 6,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    '${achievement.progress}/${achievement.target}',
                    style: TerminalTheme.terminalText.copyWith(fontSize: 10),
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }

  String _formatDate(DateTime date) {
    return '${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}';
  }
}

class Achievement {
  final String id;
  final String title;
  final String description;
  final String icon;
  final bool isUnlocked;
  final DateTime? unlockedDate;
  final int progress;
  final int target;

  Achievement({
    required this.id,
    required this.title,
    required this.description,
    required this.icon,
    required this.isUnlocked,
    this.unlockedDate,
    required this.progress,
    required this.target,
  });
}