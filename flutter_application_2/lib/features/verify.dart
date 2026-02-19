import 'dart:async'; // Keep this!
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';

class Verify extends StatefulWidget {
  const Verify({super.key});

  @override
  State<Verify> createState() => _VerifyState();
}

class _VerifyState extends State<Verify> {
  Timer? timer; // This is our "Automatic Checker"

  @override
  void initState() {
    super.initState();
    sendverifylink();

    // Start a timer that runs every 3 seconds to check if they verified
    timer = Timer.periodic(
      const Duration(seconds: 3),
      (_) => checkEmailVerified(),
    );
  }

  @override
  void dispose() {
    timer?.cancel(); // CRITICAL: Stop the timer when the user leaves the screen
    super.dispose();
  }

  Future<void> checkEmailVerified() async {
    final user = FirebaseAuth.instance.currentUser;
    if (user != null) {
      await user.reload(); // Refresh user data from Firebase
      if (user.emailVerified) {
        timer?.cancel(); // Stop checking
        if (!mounted) return;
        Navigator.pushReplacementNamed(context, '/home'); // Seamlessly go home!
      }
    }
  }

  Future<void> sendverifylink() async {
    try {
      final user = FirebaseAuth.instance.currentUser;
      if (user != null) {
        await user.sendEmailVerification();
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Verification link sent. Check your email.'),
          ),
        );
      }
    } catch (e) {
      debugPrint("Error sending link: $e");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Verify Email")),
      body: Padding(
        padding: const EdgeInsets.all(28.0),
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(
                Icons.mark_email_unread_outlined,
                size: 80,
                color: Colors.blue,
              ),
              const SizedBox(height: 20),
              const Text(
                'We sent a link! Once you tap it in your email, we\'ll automatically move you to the home screen.',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 16),
              ),
              const SizedBox(height: 30),
              TextButton(
                onPressed: sendverifylink,
                child: const Text("Didn't get an email? Resend"),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
