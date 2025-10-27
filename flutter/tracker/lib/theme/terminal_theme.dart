import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class TerminalTheme {
  // Color scheme matching the CLI app
  static const Color primaryCyan = Color(0xFF00BCD4);
  static const Color successGreen = Color(0xFF4CAF50);
  static const Color errorRed = Color(0xFFF44336);
  static const Color warningYellow = Color(0xFFFFC107);
  static const Color stressLow = Color(0xFF4CAF50); // Green 1-3
  static const Color stressMedium = Color(0xFFFFC107); // Yellow 4-6
  static const Color stressHigh = Color(0xFFF44336); // Red 7-10
  
  // Terminal colors
  static const Color backgroundBlack = Color(0xFF000000);
  static const Color backgroundDark = Color(0xFF1E1E1E);
  static const Color textWhite = Color(0xFFFFFFFF);
  static const Color textGray = Color(0xFF9E9E9E);
  static const Color textDim = Color(0xFF757575);
  static const Color borderGray = Color(0xFF424242);
  
  // Text styles
  static TextStyle get terminalText => GoogleFonts.robotoMono(
    color: textWhite,
    fontSize: 14,
  );
  
  static TextStyle get terminalTextBold => GoogleFonts.robotoMono(
    color: textWhite,
    fontSize: 14,
    fontWeight: FontWeight.bold,
  );
  
  static TextStyle get terminalTextDim => GoogleFonts.robotoMono(
    color: textDim,
    fontSize: 14,
  );
  
  static TextStyle get terminalHeader => GoogleFonts.robotoMono(
    color: primaryCyan,
    fontSize: 16,
    fontWeight: FontWeight.bold,
  );
  
  static TextStyle get terminalSuccess => GoogleFonts.robotoMono(
    color: successGreen,
    fontSize: 14,
    fontWeight: FontWeight.bold,
  );
  
  static TextStyle get terminalError => GoogleFonts.robotoMono(
    color: errorRed,
    fontSize: 14,
    fontWeight: FontWeight.bold,
  );
  
  static TextStyle get terminalWarning => GoogleFonts.robotoMono(
    color: warningYellow,
    fontSize: 14,
    fontWeight: FontWeight.bold,
  );
  
  // Theme data
  static ThemeData get themeData => ThemeData(
    brightness: Brightness.dark,
    primaryColor: primaryCyan,
    scaffoldBackgroundColor: backgroundBlack,
    fontFamily: GoogleFonts.robotoMono().fontFamily,
    
    colorScheme: const ColorScheme.dark(
      primary: primaryCyan,
      secondary: successGreen,
      error: errorRed,
      background: backgroundBlack,
      surface: backgroundDark,
      onPrimary: backgroundBlack,
      onSecondary: backgroundBlack,
      onError: textWhite,
      onBackground: textWhite,
      onSurface: textWhite,
    ),
    
    appBarTheme: AppBarTheme(
      backgroundColor: backgroundDark,
      titleTextStyle: terminalHeader,
      iconTheme: const IconThemeData(color: primaryCyan),
    ),
    
    cardTheme: CardTheme(
      color: backgroundDark,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(0),
        side: const BorderSide(color: borderGray, width: 1),
      ),
    ),
    
    inputDecorationTheme: InputDecorationTheme(
      border: const OutlineInputBorder(
        borderSide: BorderSide(color: borderGray),
      ),
      enabledBorder: const OutlineInputBorder(
        borderSide: BorderSide(color: borderGray),
      ),
      focusedBorder: const OutlineInputBorder(
        borderSide: BorderSide(color: primaryCyan),
      ),
      labelStyle: terminalText,
      hintStyle: terminalTextDim,
      fillColor: backgroundDark,
      filled: true,
    ),
    
    textButtonTheme: TextButtonThemeData(
      style: TextButton.styleFrom(
        foregroundColor: primaryCyan,
        textStyle: terminalText,
      ),
    ),
    
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: primaryCyan,
        foregroundColor: backgroundBlack,
        textStyle: terminalTextBold,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(0)),
      ),
    ),
    
    textTheme: TextTheme(
      displayLarge: terminalHeader,
      displayMedium: terminalHeader,
      displaySmall: terminalTextBold,
      headlineMedium: terminalTextBold,
      headlineSmall: terminalText,
      titleLarge: terminalTextBold,
      titleMedium: terminalText,
      titleSmall: terminalText,
      bodyLarge: terminalText,
      bodyMedium: terminalText,
      bodySmall: terminalTextDim,
      labelLarge: terminalTextBold,
      labelMedium: terminalText,
      labelSmall: terminalTextDim,
    ),
  );
  
  // Helper methods for stress level colors
  static Color getStressColor(int level) {
    if (level <= 3) return stressLow;
    if (level <= 6) return stressMedium;
    return stressHigh;
  }
  
  // Helper methods for financial colors
  static Color getFinancialColor(double amount) {
    return amount >= 0 ? successGreen : errorRed;
  }
  
  // Icon mapping (emoji to text fallback)
  static String getIcon(String emoji, String fallback) {
    return emoji; // In mobile, we'll use emoji directly
  }
}