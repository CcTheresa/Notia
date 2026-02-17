import 'package:flutter/material.dart';
// import 'package:flutter_application_2/features/auth/auth_screens/google_login_screen.dart';
import 'package:flutter_application_2/features/auth/service/auth_method.dart';
import 'package:flutter_application_2/features/home/journal_screen.dart';
import 'package:flutter_application_2/features/home/profile.dart';
import 'package:flutter_application_2/features/advice_display.dart';
import 'package:flutter_application_2/route.dart';
import 'package:flutter_application_2/services/advice_service.dart';

class AppMainScreen extends StatefulWidget {
  const AppMainScreen({super.key});

  @override
  State<AppMainScreen> createState() => _AppMainScreenState();
}

class _AppMainScreenState extends State<AppMainScreen> {
  int _currentIndex = 0;

  // You might later inject this via constructor/provider.
  final AdviceService adviceService = AdviceService(
    baseUrl: 'http://192.168.100.15',
  );

  @override
  Widget build(BuildContext context) {
    final List<Widget> pages = [
      _HomeTab(
        adviceService: adviceService,
      ), // Home with welcome + calendar + prompts
      JournalInputScreen(adviceService: adviceService),
      const AdviceDisplayScreen(),
      const Profile(), // analytics / profile
    ];

    return Scaffold(
      appBar: AppBar(
        title: const Text('Notia'),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.logout_rounded),
            onPressed: () async {
              await GoogleSigninService.signOut();
              NavigationHelper.replaceWith(context, '/login');
            },
          ),
        ],
      ),
      body: AnimatedSwitcher(
        duration: const Duration(milliseconds: 250),
        child: pages[_currentIndex],
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        selectedItemColor: Colors.cyan.shade700,
        unselectedItemColor: Colors.grey.shade500,
        type: BottomNavigationBarType.fixed,
        showUnselectedLabels: true,
        onTap: (index) {
          setState(() => _currentIndex = index);
        },
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.home_rounded),
            label: 'Home',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.edit_note_rounded),
            label: 'Journal',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.lightbulb_rounded),
            label: 'Advice',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.bar_chart_rounded),
            label: 'Insights',
          ),
        ],
      ),
    );
  }
}

// HOME TAB UI: welcome, calendar-ish strip, expandable prompts
class _HomeTab extends StatelessWidget {
  final AdviceService adviceService;
  const _HomeTab({required this.adviceService});

  @override
  Widget build(BuildContext context) {
    final today = DateTime.now();
    final weekDays = List.generate(7, (i) {
      final date = today.subtract(Duration(days: 6 - i));
      return date;
    });

    return Container(
      color: Colors.cyan.shade50,
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Welcome row with emoji
            Row(
              children: [
                Text(
                  'Hey, welcome back 👋',
                  style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: Colors.cyan.shade900,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              'This is your guided reflection space 🍃. Take a moment to check in with yourself.',
              style: Theme.of(
                context,
              ).textTheme.bodyMedium?.copyWith(color: Colors.grey.shade700),
            ),
            const SizedBox(height: 24),

            // Simple "calendar" strip for last 7 days
            Text(
              'Check-in streak',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w600,
                color: Colors.cyan.shade800,
              ),
            ),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                boxShadow: [
                  BoxShadow(
                    color: Colors.cyan.withOpacity(0.08),
                    blurRadius: 12,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: weekDays.map((date) {
                  final isToday =
                      date.day == today.day &&
                      date.month == today.month &&
                      date.year == today.year;
                  return Column(
                    children: [
                      Text(
                        ['M', 'T', 'W', 'T', 'F', 'S', 'S'][date.weekday % 7],
                        style: TextStyle(
                          fontSize: 12,
                          color: isToday
                              ? Colors.cyan.shade800
                              : Colors.grey.shade500,
                        ),
                      ),
                      const SizedBox(height: 6),
                      Container(
                        width: 26,
                        height: 26,
                        decoration: BoxDecoration(
                          color: isToday
                              ? Colors.cyan.shade600
                              : Colors.grey.shade300,
                          shape: BoxShape.circle,
                        ),
                        alignment: Alignment.center,
                        child: Text(
                          date.day.toString(),
                          style: TextStyle(fontSize: 12, color: Colors.white),
                        ),
                      ),
                    ],
                  );
                }).toList(),
              ),
            ),

            const SizedBox(height: 24),

            // Journaling prompts as expandable cards
            Text(
              'Today’s reflection prompts',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w600,
                color: Colors.cyan.shade800,
              ),
            ),
            const SizedBox(height: 8),
            _PromptCard(
              title: 'How are you feeling today? 😊',
              body:
                  'What three emotions have been the loudest today? what might they be trying to tell you?',
              onStart: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => JournalInputScreen(
                      adviceService: adviceService,
                      initialPrompt:
                          'What three emotions have been the loudest today? what might they be trying to tell you?',
                    ),
                  ),
                );
              },
            ),

            _PromptCard(
              title: 'Gratitude moment ✨',
              body:
                  'Look around, what are you grateful for right now? Who are you grateful for?',
              onStart: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => JournalInputScreen(
                      adviceService: adviceService,
                      initialPrompt:
                          'Look around, what are you grateful for right now? Who are you grateful for?',
                    ),
                  ),
                );
              },
            ),
            _PromptCard(
              title: 'Self-kindness 💖',
              body:
                  'What is one gentle thing you can say to yourself about today, even if it didn’t go perfectly?',
              onStart: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => JournalInputScreen(
                      adviceService: adviceService,
                      initialPrompt:
                          'What is one gentle thing you can say to yourself about today, even if it didn’t go perfectly?',
                    ),
                  ),
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}

class _PromptCard extends StatelessWidget {
  final String title;
  final String body;
  final VoidCallback onStart;

  const _PromptCard({
    required this.title,
    required this.body,
    required this.onStart,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 6),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      elevation: 0,
      color: Colors.white,
      child: ExpansionTile(
        tilePadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
        childrenPadding: const EdgeInsets.symmetric(
          horizontal: 16,
          vertical: 8,
        ),
        title: Text(
          title,
          style: TextStyle(
            color: Colors.cyan.shade900,
            fontWeight: FontWeight.w600,
          ),
        ),
        children: [
          Text(body, style: TextStyle(color: Colors.grey.shade700)),
          const SizedBox(height: 8),
          Align(
            alignment: Alignment.centerRight,
            child: TextButton.icon(
              onPressed: onStart,
              icon: const Icon(Icons.edit_rounded, size: 18),
              label: const Text('Start writing'),
            ),
          ),
        ],
      ),
    );
  }
}
