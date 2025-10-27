import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../theme/terminal_theme.dart';
import '../widgets/terminal_panel.dart';

class StatsScreen extends StatelessWidget {
  const StatsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: TerminalTheme.backgroundBlack,
      appBar: AppBar(
        title: Text(
          '📈 Statistics',
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
            // Summary stats
            _buildSummaryCards(),
            const SizedBox(height: 24),
            
            // Stress level chart
            _buildStressChart(),
            const SizedBox(height: 24),
            
            // Financial chart
            _buildFinancialChart(),
            const SizedBox(height: 24),
            
            // Mood distribution
            _buildMoodChart(),
            const SizedBox(height: 24),
            
            // Productivity trends
            _buildProductivityChart(),
          ],
        ),
      ),
    );
  }

  Widget _buildSummaryCards() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Summary Statistics',
          style: TerminalTheme.terminalHeader.copyWith(fontSize: 18),
        ),
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(
              child: TerminalPanel(
                child: Column(
                  children: [
                    Text(
                      '30',
                      style: TerminalTheme.terminalHeader.copyWith(fontSize: 24),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Total Entries',
                      style: TerminalTheme.terminalText,
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: TerminalPanel(
                child: Column(
                  children: [
                    Text(
                      '7',
                      style: TerminalTheme.terminalHeader.copyWith(
                        fontSize: 24,
                        color: TerminalTheme.warningYellow,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Day Streak',
                      style: TerminalTheme.terminalText,
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: TerminalPanel(
                child: Column(
                  children: [
                    Text(
                      '\$574.50',
                      style: TerminalTheme.terminalHeader.copyWith(
                        fontSize: 24,
                        color: TerminalTheme.successGreen,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Net Balance',
                      style: TerminalTheme.terminalText,
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildStressChart() {
    return TerminalPanel(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '🧘 Stress Level Trends',
            style: TerminalTheme.terminalHeader.copyWith(fontSize: 16),
          ),
          const SizedBox(height: 16),
          SizedBox(
            height: 200,
            child: LineChart(
              LineChartData(
                gridData: FlGridData(
                  show: true,
                  drawVerticalLine: true,
                  horizontalInterval: 1,
                  verticalInterval: 1,
                  getDrawingHorizontalLine: (value) {
                    return FlLine(
                      color: TerminalTheme.borderGray.withOpacity(0.3),
                      strokeWidth: 0.5,
                    );
                  },
                  getDrawingVerticalLine: (value) {
                    return FlLine(
                      color: TerminalTheme.borderGray.withOpacity(0.3),
                      strokeWidth: 0.5,
                    );
                  },
                ),
                titlesData: FlTitlesData(
                  show: true,
                  rightTitles: const AxisTitles(
                    sideTitles: SideTitles(showTitles: false),
                  ),
                  topTitles: const AxisTitles(
                    sideTitles: SideTitles(showTitles: false),
                  ),
                  bottomTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      reservedSize: 30,
                      interval: 1,
                      getTitlesWidget: (value, meta) {
                        return Text(
                          'Day ${value.toInt()}',
                          style: TerminalTheme.terminalTextDim.copyWith(fontSize: 10),
                        );
                      },
                    ),
                  ),
                  leftTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      interval: 1,
                      reservedSize: 42,
                      getTitlesWidget: (value, meta) {
                        return Text(
                          value.toInt().toString(),
                          style: TerminalTheme.terminalTextDim.copyWith(fontSize: 10),
                        );
                      },
                    ),
                  ),
                ),
                borderData: FlBorderData(
                  show: true,
                  border: Border.all(color: TerminalTheme.borderGray),
                ),
                minX: 0,
                maxX: 11,
                minY: 0,
                maxY: 10,
                lineBarsData: [
                  LineChartBarData(
                    spots: const [
                      FlSpot(0, 3),
                      FlSpot(1, 5),
                      FlSpot(2, 4),
                      FlSpot(3, 7),
                      FlSpot(4, 6),
                      FlSpot(5, 8),
                      FlSpot(6, 5),
                      FlSpot(7, 4),
                      FlSpot(8, 3),
                      FlSpot(9, 5),
                      FlSpot(10, 6),
                    ],
                    isCurved: false,
                    gradient: LinearGradient(
                      colors: [
                        TerminalTheme.stressLow,
                        TerminalTheme.stressMedium,
                        TerminalTheme.stressHigh,
                      ],
                    ),
                    barWidth: 2,
                    isStrokeCapRound: false,
                    dotData: const FlDotData(show: true),
                    belowBarData: BarAreaData(
                      show: true,
                      gradient: LinearGradient(
                        colors: [
                          TerminalTheme.primaryCyan.withOpacity(0.1),
                          TerminalTheme.primaryCyan.withOpacity(0.05),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFinancialChart() {
    return TerminalPanel(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '💰 Financial Overview',
            style: TerminalTheme.terminalHeader.copyWith(fontSize: 16),
          ),
          const SizedBox(height: 16),
          SizedBox(
            height: 200,
            child: BarChart(
              BarChartData(
                alignment: BarChartAlignment.spaceAround,
                maxY: 200,
                gridData: FlGridData(
                  show: true,
                  drawVerticalLine: false,
                  horizontalInterval: 50,
                  getDrawingHorizontalLine: (value) {
                    return FlLine(
                      color: TerminalTheme.borderGray.withOpacity(0.3),
                      strokeWidth: 0.5,
                    );
                  },
                ),
                titlesData: FlTitlesData(
                  show: true,
                  rightTitles: const AxisTitles(
                    sideTitles: SideTitles(showTitles: false),
                  ),
                  topTitles: const AxisTitles(
                    sideTitles: SideTitles(showTitles: false),
                  ),
                  bottomTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      getTitlesWidget: (value, meta) {
                        const titles = ['Week 1', 'Week 2', 'Week 3', 'Week 4'];
                        return Text(
                          titles[value.toInt()],
                          style: TerminalTheme.terminalTextDim.copyWith(fontSize: 10),
                        );
                      },
                    ),
                  ),
                  leftTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      interval: 50,
                      reservedSize: 42,
                      getTitlesWidget: (value, meta) {
                        return Text(
                          '\$${value.toInt()}',
                          style: TerminalTheme.terminalTextDim.copyWith(fontSize: 10),
                        );
                      },
                    ),
                  ),
                ),
                borderData: FlBorderData(
                  show: true,
                  border: Border.all(color: TerminalTheme.borderGray),
                ),
                barGroups: [
                  BarChartGroupData(
                    x: 0,
                    barRods: [
                      BarChartRodData(
                        toY: 150,
                        color: TerminalTheme.successGreen,
                        width: 16,
                        borderRadius: BorderRadius.circular(0),
                      ),
                      BarChartRodData(
                        toY: -80,
                        color: TerminalTheme.errorRed,
                        width: 16,
                        borderRadius: BorderRadius.circular(0),
                      ),
                    ],
                  ),
                  BarChartGroupData(
                    x: 1,
                    barRods: [
                      BarChartRodData(
                        toY: 120,
                        color: TerminalTheme.successGreen,
                        width: 16,
                        borderRadius: BorderRadius.circular(0),
                      ),
                      BarChartRodData(
                        toY: -95,
                        color: TerminalTheme.errorRed,
                        width: 16,
                        borderRadius: BorderRadius.circular(0),
                      ),
                    ],
                  ),
                  BarChartGroupData(
                    x: 2,
                    barRods: [
                      BarChartRodData(
                        toY: 180,
                        color: TerminalTheme.successGreen,
                        width: 16,
                        borderRadius: BorderRadius.circular(0),
                      ),
                      BarChartRodData(
                        toY: -110,
                        color: TerminalTheme.errorRed,
                        width: 16,
                        borderRadius: BorderRadius.circular(0),
                      ),
                    ],
                  ),
                  BarChartGroupData(
                    x: 3,
                    barRods: [
                      BarChartRodData(
                        toY: 140,
                        color: TerminalTheme.successGreen,
                        width: 16,
                        borderRadius: BorderRadius.circular(0),
                      ),
                      BarChartRodData(
                        toY: -75,
                        color: TerminalTheme.errorRed,
                        width: 16,
                        borderRadius: BorderRadius.circular(0),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                width: 12,
                height: 12,
                color: TerminalTheme.successGreen,
              ),
              const SizedBox(width: 4),
              Text(
                'Income',
                style: TerminalTheme.terminalTextDim.copyWith(fontSize: 12),
              ),
              const SizedBox(width: 16),
              Container(
                width: 12,
                height: 12,
                color: TerminalTheme.errorRed,
              ),
              const SizedBox(width: 4),
              Text(
                'Expenses',
                style: TerminalTheme.terminalTextDim.copyWith(fontSize: 12),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildMoodChart() {
    return TerminalPanel(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '😊 Mood Distribution',
            style: TerminalTheme.terminalHeader.copyWith(fontSize: 16),
          ),
          const SizedBox(height: 16),
          SizedBox(
            height: 150,
            child: PieChart(
              PieChartData(
                sectionsSpace: 2,
                centerSpaceRadius: 40,
                sections: [
                  PieChartSectionData(
                    color: TerminalTheme.successGreen,
                    value: 35,
                    title: '35%\nGood',
                    radius: 50,
                    titleStyle: TerminalTheme.terminalTextBold.copyWith(fontSize: 12),
                  ),
                  PieChartSectionData(
                    color: TerminalTheme.primaryCyan,
                    value: 25,
                    title: '25%\nExcellent',
                    radius: 50,
                    titleStyle: TerminalTheme.terminalTextBold.copyWith(fontSize: 12),
                  ),
                  PieChartSectionData(
                    color: TerminalTheme.warningYellow,
                    value: 30,
                    title: '30%\nNeutral',
                    radius: 50,
                    titleStyle: TerminalTheme.terminalTextBold.copyWith(fontSize: 12),
                  ),
                  PieChartSectionData(
                    color: TerminalTheme.errorRed,
                    value: 10,
                    title: '10%\nPoor',
                    radius: 50,
                    titleStyle: TerminalTheme.terminalTextBold.copyWith(fontSize: 12),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildProductivityChart() {
    return TerminalPanel(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '📊 Productivity Score',
            style: TerminalTheme.terminalHeader.copyWith(fontSize: 16),
          ),
          const SizedBox(height: 16),
          SizedBox(
            height: 120,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                _buildMetricCard('Tasks Completed', '24', TerminalTheme.successGreen),
                _buildMetricCard('Avg Focus Time', '6.5h', TerminalTheme.primaryCyan),
                _buildMetricCard('Productivity %', '78%', TerminalTheme.warningYellow),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMetricCard(String label, String value, Color color) {
    return Expanded(
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 4),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: TerminalTheme.backgroundDark,
          border: Border.all(color: color),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              value,
              style: TerminalTheme.terminalHeader.copyWith(
                color: color,
                fontSize: 20,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: TerminalTheme.terminalTextDim.copyWith(fontSize: 10),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}