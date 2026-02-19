import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:get/get.dart';
import 'firebase_options.dart';

// Imported all screens so main knows they exist
import 'package:flutter_application_2/features/login.dart';
import 'package:flutter_application_2/features/signup.dart';
import 'package:flutter_application_2/features/verify.dart';
import 'package:flutter_application_2/features/home/app_main_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform);
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return GetMaterialApp(
      title: 'Notia',
      debugShowCheckedModeBanner: false,
      // 1. Initial Screen
      home: const Login(),

      // 2. The Route Map (This stops the "Unexpected Error")
      routes: {
        '/login': (context) => const Login(),
        '/signup': (context) => const Signup(),
        '/verify': (context) => const Verify(),
        '/home': (context) => const AppMainScreen(),
      },
    );
  }
}
