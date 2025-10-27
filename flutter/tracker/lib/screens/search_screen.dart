import 'package:flutter/material.dart';
import '../theme/terminal_theme.dart';
import '../widgets/terminal_panel.dart';
import '../widgets/terminal_table.dart';

class SearchScreen extends StatefulWidget {
  const SearchScreen({super.key});

  @override
  State<SearchScreen> createState() => _SearchScreenState();
}

class _SearchScreenState extends State<SearchScreen> {
  final _searchController = TextEditingController();
  DateTime? _startDate;
  DateTime? _endDate;
  String _searchType = 'text'; // 'text', 'date', 'both'
  bool _isSearching = false;
  
  // Sample search results
  List<List<String>> _searchResults = [];

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  void _performSearch() {
    setState(() {
      _isSearching = true;
    });

    // Simulate search delay
    Future.delayed(const Duration(seconds: 1), () {
      // Sample search results based on search type
      if (_searchType == 'date' && _startDate != null) {
        _searchResults = [
          ['2024-01-15', '\$50.00', '7', 'Meeting with client', 'Good'],
          ['2024-01-14', '-\$25.50', '4', 'Team lunch', 'Neutral'],
          ['2024-01-13', '\$100.00', '2', 'Project completion', 'Excellent'],
        ];
      } else if (_searchController.text.isNotEmpty) {
        _searchResults = [
          ['2024-01-15', '\$50.00', '7', 'Meeting with **client**', 'Good'],
          ['2024-01-12', '\$0.00', '8', '**Client** presentation', 'Poor'],
          ['2024-01-10', '\$75.00', '3', 'Follow up with **client**', 'Good'],
        ];
      } else {
        _searchResults = [];
      }

      setState(() {
        _isSearching = false;
      });
    });
  }

  Future<void> _selectDateRange() async {
    final DateTimeRange? range = await showDateRangePicker(
      context: context,
      firstDate: DateTime(2020),
      lastDate: DateTime.now(),
      builder: (context, child) {
        return Theme(
          data: Theme.of(context).copyWith(
            colorScheme: const ColorScheme.dark(
              primary: TerminalTheme.primaryCyan,
              onPrimary: TerminalTheme.backgroundBlack,
              surface: TerminalTheme.backgroundDark,
              onSurface: TerminalTheme.textWhite,
            ),
          ),
          child: child!,
        );
      },
    );

    if (range != null) {
      setState(() {
        _startDate = range.start;
        _endDate = range.end;
        _searchType = 'date';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: TerminalTheme.backgroundBlack,
      appBar: AppBar(
        title: Text(
          '🔍 Search',
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
            // Search type selector
            Text(
              'Search Type',
              style: TerminalTheme.terminalTextBold,
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                ChoiceChip(
                  label: Text(
                    'Text Search',
                    style: TerminalTheme.terminalText.copyWith(
                      color: _searchType == 'text' 
                          ? TerminalTheme.backgroundBlack 
                          : TerminalTheme.textWhite,
                    ),
                  ),
                  selected: _searchType == 'text',
                  onSelected: (selected) {
                    setState(() {
                      _searchType = 'text';
                    });
                  },
                  backgroundColor: TerminalTheme.backgroundDark,
                  selectedColor: TerminalTheme.primaryCyan,
                ),
                const SizedBox(width: 8),
                ChoiceChip(
                  label: Text(
                    'Date Range',
                    style: TerminalTheme.terminalText.copyWith(
                      color: _searchType == 'date' 
                          ? TerminalTheme.backgroundBlack 
                          : TerminalTheme.textWhite,
                    ),
                  ),
                  selected: _searchType == 'date',
                  onSelected: (selected) {
                    setState(() {
                      _searchType = 'date';
                    });
                  },
                  backgroundColor: TerminalTheme.backgroundDark,
                  selectedColor: TerminalTheme.primaryCyan,
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Search input area
            if (_searchType == 'text') ...[
              Text(
                'Search Text',
                style: TerminalTheme.terminalTextBold,
              ),
              const SizedBox(height: 8),
              TextField(
                controller: _searchController,
                style: TerminalTheme.terminalText,
                decoration: InputDecoration(
                  hintText: 'Enter keywords, notes, or descriptions...',
                  hintStyle: TerminalTheme.terminalTextDim,
                  border: const OutlineInputBorder(),
                  enabledBorder: OutlineInputBorder(
                    borderSide: BorderSide(color: TerminalTheme.borderGray),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderSide: BorderSide(color: TerminalTheme.primaryCyan),
                  ),
                ),
                onSubmitted: (_) => _performSearch(),
              ),
            ] else ...[
              Text(
                'Date Range',
                style: TerminalTheme.terminalTextBold,
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  Expanded(
                    child: TextButton(
                      onPressed: _selectDateRange,
                      style: TextButton.styleFrom(
                        backgroundColor: TerminalTheme.backgroundDark,
                        side: BorderSide(color: TerminalTheme.borderGray),
                        padding: const EdgeInsets.symmetric(vertical: 12),
                      ),
                      child: Text(
                        _startDate == null
                            ? 'Select Date Range'
                            : '${_formatDate(_startDate!)} - ${_formatDate(_endDate!)}',
                        style: TerminalTheme.terminalText,
                      ),
                    ),
                  ),
                  if (_startDate != null) ...[
                    const SizedBox(width: 8),
                    IconButton(
                      onPressed: () {
                        setState(() {
                          _startDate = null;
                          _endDate = null;
                        });
                      },
                      icon: const Icon(Icons.clear),
                      color: TerminalTheme.errorRed,
                    ),
                  ],
                ],
              ),
            ],
            const SizedBox(height: 16),

            // Search button
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _isSearching ? null : _performSearch,
                child: _isSearching
                    ? Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              valueColor: AlwaysStoppedAnimation<Color>(
                                TerminalTheme.backgroundBlack,
                              ),
                            ),
                          ),
                          const SizedBox(width: 8),
                          Text(
                            'Searching...',
                            style: TerminalTheme.terminalTextBold.copyWith(
                              color: TerminalTheme.backgroundBlack,
                            ),
                          ),
                        ],
                      )
                    : Text(
                        'Search',
                        style: TerminalTheme.terminalTextBold,
                      ),
              ),
            ),
            const SizedBox(height: 24),

            // Results header
            if (_searchResults.isNotEmpty) ...[
              Text(
                'Search Results',
                style: TerminalTheme.terminalHeader.copyWith(fontSize: 16),
              ),
              const SizedBox(height: 8),
              Text(
                '${_searchResults.length} entries found',
                style: TerminalTheme.terminalTextDim,
              ),
              const SizedBox(height: 16),
            ],

            // Search results
            Expanded(
              child: _searchResults.isEmpty && !_isSearching
                  ? Center(
                      child: Text(
                        'No results yet. Try searching for something!',
                        style: TerminalTheme.terminalTextDim,
                        textAlign: TextAlign.center,
                      ),
                    )
                  : _searchResults.isEmpty && _isSearching
                      ? const Center()
                      : TerminalPanel(
                          child: TerminalTable(
                            headers: ['Date', 'Finance', 'Stress', 'Notes', 'Mood'],
                            rows: _searchResults,
                            rowColors: _searchResults.map((row) {
                              final stressLevel = int.parse(row[2]);
                              return TerminalTheme.getStressColor(stressLevel);
                            }).toList(),
                          ),
                        ),
            ),
          ],
        ),
      ),
    );
  }

  String _formatDate(DateTime date) {
    return '${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}';
  }
}