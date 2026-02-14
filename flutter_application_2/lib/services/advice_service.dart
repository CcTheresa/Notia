import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/advice_response.dart';

class AdviceService {
  final String baseUrl;

  AdviceService({required this.baseUrl});

  Future<AdviceResponse> getAdvice(String journalEntry) async {
    final url = Uri.parse('$baseUrl/get-advice');
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'text': journalEntry}),
    );

    if (response.statusCode == 200) {
      return AdviceResponse.fromJson(jsonDecode(response.body));
    } else {
      throw Exception(
        'Failed to fetch advice: ${response.statusCode} ${response.reasonPhrase}',
      );
    }
  }
}
