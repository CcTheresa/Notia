import 'package:flutter/material.dart';
import '../models/advice_response.dart';
import '../services/reflection_service.dart';

class LayerStyle {
  final String title;
  final Color bg;
  final Color accent;
  final IconData icon;

  const LayerStyle({
    required this.title,
    required this.bg,
    required this.accent,
    required this.icon,
  });
}

const Map<String, LayerStyle> layerStyles = {
  'validation': LayerStyle(
    title: 'First, let’s validate this',
    bg: Color(0xFFE6F6FF),
    accent: Color(0xFF0284C7),
    icon: Icons.favorite,
  ),
  'psychoeducation': LayerStyle(
    title: 'Understanding what’s happening',
    bg: Color(0xFFF3E8FF),
    accent: Color(0xFF7C3AED),
    icon: Icons.lightbulb,
  ),
  'technique': LayerStyle(
    title: 'Try this gentle technique',
    bg: Color(0xFFEFFDF5),
    accent: Color(0xFF16A34A),
    icon: Icons.self_improvement,
  ),
  'reframing': LayerStyle(
    title: 'Gently reframe the story',
    bg: Color(0xFFFFF7ED),
    accent: Color(0xFFEA580C),
    icon: Icons.change_circle,
  ),
  'journaling': LayerStyle(
    title: 'A prompt to reflect with',
    bg: Color(0xFFFDF2FF),
    accent: Color(0xFFDB2777),
    icon: Icons.edit,
  ),
};

class AdviceDisplayScreen extends StatefulWidget {
  const AdviceDisplayScreen({super.key});

  @override
  _AdviceDisplayScreenState createState() => _AdviceDisplayScreenState();
}

class _AdviceDisplayScreenState extends State<AdviceDisplayScreen> {
  late AdviceResponse adviceResponse;
  late List<String> layerKeys;
  late String _journalText;
  int currentIndex = 0;
  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final args = ModalRoute.of(context)!.settings.arguments;

    if (args != null && args is Map<String, dynamic>) {
      adviceResponse = AdviceResponse.fromJson(
        args['advice'] as Map<String, dynamic>,
      );
      _journalText = args['journalText'] as String? ?? '';
      layerKeys = adviceResponse.adviceLayers.keys.toList();
    } else {
      adviceResponse = AdviceResponse(
        detectedEmotions: [],
        matchedIssue: '',
        matchedSubIssue: '',
        confidence: 0.0,
        emotionOverlap: [],
        adviceLayers: {},
      );
      _journalText = '';
      layerKeys = [];
    }
  }

  void _goToPrevious() {
    if (currentIndex > 0) setState(() => currentIndex--);
  }

  void _goToNext() {
    if (currentIndex < layerKeys.length - 1) setState(() => currentIndex++);
  }

  @override
  Widget build(BuildContext context) {
    if (layerKeys.isEmpty) {
      return Scaffold(
        appBar: AppBar(title: const Text('Guided Reflection')),
        body: const Center(child: Text('No advice data available.')),
      );
    }

    final currentKey = layerKeys[currentIndex];
    final currentLayer = adviceResponse.adviceLayers[currentKey]!;
    final style =
        layerStyles[currentKey] ??
        LayerStyle(
          title: currentKey.capitalize(),
          bg: Colors.grey.shade100,
          accent: Colors.grey.shade700,
          icon: Icons.notes,
        );

    final total = layerKeys.length;
    final step = currentIndex + 1;
    final isLast = step == total;

    return Scaffold(
      appBar: AppBar(title: const Text('Guided Reflection')),
      body: Container(
        color: const Color(0xFFF7FAFC),
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            _buildHeader(),
            const SizedBox(height: 12),
            _buildProgressBar(style.accent, step, total),
            const SizedBox(height: 16),
            Expanded(
              child: SingleChildScrollView(
                child: Container(
                  decoration: BoxDecoration(
                    color: style.bg,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(style.icon, color: style.accent),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              style.title,
                              style: TextStyle(
                                color: style.accent,
                                fontSize: 18,
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      Text(
                        currentLayer.text,
                        style: const TextStyle(fontSize: 15, height: 1.4),
                      ),
                    ],
                  ),
                ),
              ),
            ),
            const SizedBox(height: 12),
            _buildBottomButtons(isLast),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader() {
    final topEmotions = adviceResponse.detectedEmotions.take(3).toList();
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (topEmotions.isNotEmpty)
          Wrap(
            spacing: 8,
            runSpacing: 4,
            children: topEmotions.map((e) {
              return Chip(
                backgroundColor: const Color(0xFFE5F4FF),
                label: Text(
                  e.emotion.capitalize(),
                  style: const TextStyle(fontSize: 12),
                ),
              );
            }).toList(),
          ),
        const SizedBox(height: 6),
        if (adviceResponse.matchedIssue.isNotEmpty)
          Text(
            'Focus: ${adviceResponse.matchedIssue.replaceAll('_', ' ').capitalize()}',
            style: TextStyle(fontSize: 13, color: Colors.grey.shade700),
          ),
      ],
    );
  }

  Widget _buildProgressBar(Color accent, int step, int total) {
    return Column(
      children: [
        LinearProgressIndicator(
          value: step / total,
          backgroundColor: Colors.grey.shade200,
          color: accent,
        ),
        const SizedBox(height: 4),
        Text(
          'Step $step of $total',
          style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
        ),
      ],
    );
  }

  Widget _buildBottomButtons(bool isLast) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        TextButton(
          onPressed: currentIndex > 0 ? _goToPrevious : null,
          child: const Text('Back'),
        ),
        ElevatedButton(
          onPressed: () async {
            if (!isLast) {
              _goToNext();
            } else {
              try {
                await ReflectionService.saveReflection(
                  journalText: _journalText,
                  advice: adviceResponse,
                );

                if (!mounted) return;
                Navigator.pushNamed(context, '/profile');
              } catch (e) {
                // so it doesn’t silently fail
                if (!mounted) return;
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('Could not save reflection: $e')),
                );
                // still allow navigation so you can see Insights
                Navigator.pushNamed(context, '/profile');
              }
            }
          },
          child: Text(isLast ? 'View Analysis' : 'Next'),
        ),
      ],
    );
  }
}

extension StringCasingExtension on String {
  String capitalize() =>
      isEmpty ? this : '${this[0].toUpperCase()}${substring(1)}';
}
