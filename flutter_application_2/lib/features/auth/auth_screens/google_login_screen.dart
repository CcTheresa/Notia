import 'package:flutter/material.dart';
import 'package:flutter_application_2/features/auth/service/auth_method.dart';

class GoogleLoginScreen extends StatefulWidget {
  const GoogleLoginScreen({super.key});

  @override
  State<GoogleLoginScreen> createState() => _GoogleLoginScreenState();
}

class _GoogleLoginScreenState extends State<GoogleLoginScreen> {
  bool _isLoading = false;

  //sign in with google method

  Future<void> _signInWithGoogle() async {
    setState(() {
      _isLoading = true;
    });

    try {
      final userCredential = await GoogleSigninService.signInWithGoogle();
      if (!mounted) return;

      if (userCredential != null) {
        // Navigate to the home screen
        //successful sign in navigate to main screen
        Navigator.pushNamedAndRemoveUntil(context, '/home', (route) => false);

        debugPrint(
          'Google Sign-In successful: ${userCredential.user?.displayName}',
        );
      }
    } catch (e) {
      if (!mounted) return;
      // Handle errors here
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text("Google Sign-In failed. Please try again."),
          backgroundColor: Colors.red,
          behavior: SnackBarBehavior.floating,
        ),
      );

      debugPrint('Sign in error: $e');
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    Size size = MediaQuery.of(context).size;
    return Scaffold(
      backgroundColor: Colors.white,
      body: SafeArea(
        child: Column(
          children: [
            Image.asset(
              "assets/images/g_logo.png",
              height: size.height * 0.56,
              fit: BoxFit.cover,
            ),
            SizedBox(height: size.height * 0.13),
            _isLoading
                ? CircularProgressIndicator()
                : GestureDetector(
                    onTap: _signInWithGoogle,
                    child: Image.asset(
                      'assets/images/Sign_in_logo.png',
                      height: 48, // adjust size as needed
                      fit: BoxFit.contain,
                    ),
                  ),
          ],
        ),
      ),
    );
  }
}
