import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';

class Signup extends StatefulWidget {
  const Signup({super.key});

  @override
  State<Signup> createState() => _SignupState();
}

class _SignupState extends State<Signup> {
  final _formKey = GlobalKey<FormState>(); // For validation
  final TextEditingController email = TextEditingController();
  final TextEditingController password = TextEditingController();
  bool _isObscured = true; // Visibility toggle state

  // The Regex Validator
  String? validatePassword(String? value) {
    if (value == null || value.isEmpty) return 'Please enter a password';
    RegExp regex = RegExp(
      r'^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[!@#\$&*~]).{8,}$',
    );
    if (!regex.hasMatch(value)) {
      return '8+ chars, 1 Uppercase, 1 Number, 1 Special character';
    }
    return null;
  }

  Future<void> signup() async {
    // Only run if the form validation passes
    if (_formKey.currentState!.validate()) {
      try {
        await FirebaseAuth.instance.createUserWithEmailAndPassword(
          email: email.text.trim(),
          password: password.text.trim(),
        );

        if (!mounted) return;
        // After successful creation, send them to verify
        Navigator.pushReplacementNamed(context, '/verify');
      } on FirebaseAuthException catch (e) {
        String msg;
        if (e.code == 'email-already-in-use') {
          msg = 'An account with this email already exists.';
        } else if (e.code == 'weak-password') {
          msg = 'Password is too weak.';
        } else if (e.code == 'invalid-email') {
          msg = 'Invalid email format.';
        } else {
          msg = 'Signup failed: ${e.message}';
        }

        if (!mounted) return;
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(msg)));
      } catch (e) {
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Unexpected error, please try again.')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Sign up")),
      body: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Form(
          // Wrap in Form widget!
          key: _formKey,
          child: Column(
            children: [
              TextFormField(
                // Use TextFormField, not TextField
                controller: email,
                decoration: const InputDecoration(
                  labelText: "Email",
                  prefixIcon: Icon(Icons.email_outlined),
                ),
              ),
              const SizedBox(height: 15),
              TextFormField(
                controller: password,
                obscureText: _isObscured,
                validator: validatePassword, // Attach validator here
                decoration: InputDecoration(
                  labelText: "Password",
                  prefixIcon: const Icon(Icons.lock_outline),
                  suffixIcon: IconButton(
                    icon: Icon(
                      _isObscured ? Icons.visibility : Icons.visibility_off,
                    ),
                    onPressed: () => setState(() => _isObscured = !_isObscured),
                  ),
                ),
              ),
              const SizedBox(height: 30),
              ElevatedButton(
                style: ElevatedButton.styleFrom(
                  minimumSize: const Size.fromHeight(50),
                ),
                onPressed: signup,
                child: const Text("Sign up"),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
