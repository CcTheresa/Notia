import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:flutter_application_2/features/auth/auth_screens/google_login_screen.dart';
import 'package:flutter_application_2/features/login.dart';
import 'firebase_options.dart';
import 'services/advice_service.dart';
import 'package:flutter_application_2/features/home/app_main_screen.dart';
import 'features/home/journal_screen.dart';
import 'features/advice_display.dart';
import 'features/home/profile.dart';
import 'features/verify.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform);

  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  final AdviceService adviceService = AdviceService(
    baseUrl: 'http://10.5.63.115:8000',
  );

  MyApp({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Notia',
      theme: ThemeData(primarySwatch: Colors.cyan),
      initialRoute: '/login',
      routes: {
        '/login': (context) => Login(),
        '/googleLogin': (context) => GoogleLoginScreen(),
        '/home': (context) => AppMainScreen(),
        '/journal': (context) =>
            JournalInputScreen(adviceService: adviceService),
        '/advice': (context) => AdviceDisplayScreen(),
        '/profile': (context) => Profile(),
        '/verify': (context) => Verify(),
      },
    );
  }
}
