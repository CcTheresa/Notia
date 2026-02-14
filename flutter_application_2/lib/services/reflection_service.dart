import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';

import '../models/advice_response.dart';
import '../models/reflection_entry.dart';

class ReflectionService {
  static final _firestore = FirebaseFirestore.instance;
  static final _auth = FirebaseAuth.instance;

  static CollectionReference<Map<String, dynamic>> _userReflectionsCol() {
    final uid = _auth.currentUser?.uid;
    if (uid == null) {
      throw Exception('No user logged in');
    }
    return _firestore.collection('users').doc(uid).collection('reflections');
  }

  static Future<void> saveReflection({
    required String journalText,
    required AdviceResponse advice,
  }) async {
    final topEmotions = advice.detectedEmotions
        .take(3)
        .map((e) => e.emotion)
        .toList();

    final docRef = _userReflectionsCol().doc();

    final entry = ReflectionEntry(
      id: docRef.id,
      journalText: journalText,
      createdAt: DateTime.now(),
      emotions: topEmotions,
      issue: advice.matchedIssue,
      subIssue: advice.matchedSubIssue,
    );

    await docRef.set(entry.toMap());
  }

  static Stream<List<ReflectionEntry>> reflectionsStream() {
    return _userReflectionsCol()
        .orderBy('createdAt', descending: true)
        .snapshots()
        .map(
          (snap) => snap.docs
              .map((d) => ReflectionEntry.fromDoc(d.id, d.data()))
              .toList(),
        );
  }
}
