import 'package:flutter/material.dart';
import '../../services/advice_service.dart'; // Your service file
import '../../models/advice_response.dart'; // Adjust path if different

class JournalInputScreen extends StatefulWidget {
  final AdviceService adviceService;
  final String? initialPrompt;

  // Constructor with a required parameter to initialize the final field
  const JournalInputScreen({
    super.key,
    required this.adviceService,
    this.initialPrompt,
  });

  @override
  _JournalInputScreenState createState() => _JournalInputScreenState();
}

class _JournalInputScreenState extends State<JournalInputScreen> {
  final TextEditingController _controller = TextEditingController();
  bool _isLoading = false;
  String? _errorMessage;

  void _submitEntry() async {
    final text = _controller.text.trim();
    if (text.isEmpty) {
      setState(() {
        _errorMessage = "Please enter your journal text.";
      });
      return;
    }
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    print('>>> Calling getAdvice with text length ${text.length}');
    print('>>> Using baseUrl: ${widget.adviceService.baseUrl}');

    try {
      //get advice from adviceresonse
      AdviceResponse adviceResponse = await widget.adviceService.getAdvice(
        text,
      );
      print('>>> Received advice response');

      setState(() {
        _isLoading = false;
      });

      // Assuming adviceResponse can be converted to Map<String, dynamic>
      final adviceJson = adviceResponse.toJson();

      Navigator.pushNamed(
        context,
        '/advice',
        arguments: {'advice': adviceJson, 'journalText': text},
      );
    } catch (e) {
      print('>>> Error while fetching advice: $e');

      setState(() {
        _isLoading = false;
        _errorMessage = "Failed to get advice. Please try again.";
      });
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Journal Entry')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextField(
              controller: _controller,
              maxLines: 8,
              decoration: InputDecoration(
                //use prompt if provided
                hintText:
                    widget.initialPrompt ??
                    'Hey, how are you feeling today ☺️?',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 12),
            if (_errorMessage != null)
              Text(_errorMessage!, style: TextStyle(color: Colors.red)),
            const SizedBox(height: 12),
            _isLoading
                ? CircularProgressIndicator()
                : ElevatedButton(
                    onPressed: _submitEntry,
                    child: Text('What do you think?'),
                  ),
          ],
        ),
      ),
    );
  }
}
