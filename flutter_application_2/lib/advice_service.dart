import 'dart:convert';
import 'package:http/http.dart' as http;

// Data models representing the API response (simplified)
class Emotion {
  final String emotion;
  final double confidence;
  Emotion({required this.emotion, required this.confidence});
  factory Emotion.fromJson(Map<String, dynamic> json) {
    return Emotion(
      emotion: json['emotion'],
      confidence: (json['confidence'] as num).toDouble(),
    );
  }
}

class AdviceLayer {
  final String text;
  final List<String> emotions;
  AdviceLayer({required this.text, required this.emotions});
  factory AdviceLayer.fromJson(Map<String, dynamic> json) {
    return AdviceLayer(
      text: json['text'],
      emotions: List<String>.from(json['emotions']),
    );
  }
}

class AdviceResponse {
  final List<Emotion> detectedEmotions;
  final String matchedIssue;
  final String matchedSubIssue;
  final double confidence;
  final List<String> emotionOverlap;
  final Map<String, AdviceLayer> adviceLayers;

  AdviceResponse({
    required this.detectedEmotions,
    required this.matchedIssue,
    required this.matchedSubIssue,
    required this.confidence,
    required this.emotionOverlap,
    required this.adviceLayers,
  });

  factory AdviceResponse.fromJson(Map<String, dynamic> json) {
    var emotionsJson = json['detected_emotions'] as List;
    var emotionsList = emotionsJson.map((e) => Emotion.fromJson(e)).toList();

    Map<String, AdviceLayer> layers = {};
    Map<String, dynamic> layersJson = json['advice_layers'];
    layersJson.forEach((key, value) {
      layers[key] = AdviceLayer.fromJson(value);
    });

    return AdviceResponse(
      detectedEmotions: emotionsList,
      matchedIssue: json['matched_issue'],
      matchedSubIssue: json['matched_sub_issue'],
      confidence: (json['confidence'] as num).toDouble(),
      emotionOverlap: List<String>.from(json['emotion_overlap']),
      adviceLayers: layers,
    );
  }
}

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
