import 'package:cloud_firestore/cloud_firestore.dart';

class ReflectionEntry {
  final String id;
  final String journalText;
  final DateTime createdAt;
  final List<String> emotions;
  final String issue;
  final String subIssue;

  ReflectionEntry({
    required this.id,
    required this.journalText,
    required this.createdAt,
    required this.emotions,
    required this.issue,
    required this.subIssue,
  });

  Map<String, dynamic> toMap() {
    return {
      'journalText': journalText,
      'createdAt': createdAt.toUtc(),
      'emotions': emotions,
      'issue': issue,
      'subIssue': subIssue,
    };
  }

  static ReflectionEntry fromDoc(String id, Map<String, dynamic> data) {
    return ReflectionEntry(
      id: id,
      journalText: data['journalText'] as String? ?? '',
      createdAt: (data['createdAt'] as Timestamp).toDate(),
      emotions: List<String>.from(data['emotions'] ?? []),
      issue: data['issue'] as String? ?? '',
      subIssue: data['subIssue'] as String? ?? '',
    );
  }
}
