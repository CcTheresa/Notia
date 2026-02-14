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

  Map<String, dynamic> toJson() => {
    'emotion': emotion,
    'confidence': confidence,
  };
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

  Map<String, dynamic> toJson() => {'text': text, 'emotions': emotions};
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

  Map<String, dynamic> toJson() {
    return {
      'detected_emotions': detectedEmotions.map((e) => e.toJson()).toList(),
      'matched_issue': matchedIssue,
      'matched_sub_issue': matchedSubIssue,
      'confidence': confidence,
      'emotion_overlap': emotionOverlap,
      'advice_layers': adviceLayers.map((k, v) => MapEntry(k, v.toJson())),
    };
  }
}
