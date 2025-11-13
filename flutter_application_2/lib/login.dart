import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:flutter_application_2/forgot.dart';
import 'package:flutter_application_2/signup.dart';
import 'package:get/get.dart';

class Login extends StatefulWidget {
  const Login({super.key});

  @override
  State<Login> createState() => _LoginState();
}

class _LoginState extends State<Login> {
  TextEditingController email = TextEditingController();
  TextEditingController password = TextEditingController();

  bool isloading = false;

  signIn() async {
    setState(() {
      isloading = true;
    });
    try {
      await FirebaseAuth.instance.signInWithEmailAndPassword(
        email: email.text,
        password: password.text,
      );
      // ✅ Success — navigate to home or show success message
      Get.snackbar(
        "Success",
        "Logged in successfully!",
        snackPosition: SnackPosition.BOTTOM,
        backgroundColor: Colors.green.withOpacity(0.8),
        colorText: Colors.white,
      );
    } on FirebaseAuthException catch (e) {
      // Handle specific Firebase errors with user-friendly messages
      String errorMessage = '';

      if (e.code == 'user-not-found') {
        errorMessage =
            'No account found with this email. Please sign up first.';
      } else if (e.code == 'wrong-password') {
        errorMessage = 'Incorrect password. Please try again.';
      } else if (e.code == 'invalid-email') {
        errorMessage = 'Invalid email address format.';
      } else if (e.code == 'user-disabled') {
        errorMessage = 'This account has been disabled.';
      } else if (e.code == 'invalid-credential') {
        errorMessage =
            'Invalid credentials. Please check your email and password or sign up.';
      } else {
        errorMessage = 'Login failed: ${e.message}';
      }
      Get.snackbar("Error", errorMessage);
    } catch (e) {
      Get.snackbar(
        "Error",
        "An unexpected error occurred. Please try again.",
        snackPosition: SnackPosition.BOTTOM,
        backgroundColor: Colors.red.withOpacity(0.8),
        colorText: Colors.white,
      );
    }
    setState(() {
      isloading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return isloading
        ? Center(child: CircularProgressIndicator())
        : Scaffold(
            appBar: AppBar(title: Text("Login")),
            body: Padding(
              padding: const EdgeInsets.all(20.0),
              child: Column(
                children: [
                  TextField(
                    controller: email,
                    decoration: InputDecoration(hintText: "Enter Email"),
                  ),
                  TextField(
                    controller: password,
                    decoration: InputDecoration(hintText: "Enter Password"),
                  ),

                  ElevatedButton(
                    onPressed: (() => signIn()),
                    child: Text("Login"),
                  ),
                  SizedBox(height: 30),
                  ElevatedButton(
                    onPressed: (() => Get.to(Signup())),
                    child: Text("Register now"),
                  ),
                  SizedBox(height: 30),
                  ElevatedButton(
                    onPressed: (() => Get.to(Forgot())),
                    child: Text("Forgot Password ?"),
                  ),
                ],
              ),
            ),
          );
  }
}
