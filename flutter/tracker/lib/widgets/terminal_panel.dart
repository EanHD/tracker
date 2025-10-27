import 'package:flutter/material.dart';
import '../theme/terminal_theme.dart';

class TerminalPanel extends StatelessWidget {
  final Widget child;
  final EdgeInsetsGeometry? padding;
  final bool isNarrow;
  
  const TerminalPanel({
    super.key,
    required this.child,
    this.padding,
    this.isNarrow = false,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: padding ?? (isNarrow 
          ? const EdgeInsets.fromLTRB(1, 1, 1, 1) 
          : const EdgeInsets.fromLTRB(1, 2, 1, 2)),
      decoration: BoxDecoration(
        color: TerminalTheme.backgroundDark,
        border: Border.all(
          color: TerminalTheme.primaryCyan,
          width: 1,
        ),
        borderRadius: BorderRadius.circular(0),
      ),
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: child,
      ),
    );
  }
}