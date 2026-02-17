import 'package:flutter/material.dart';

class NavigationHelper {
  // Push a named route (The "GPS" way)
  static void navigateTo(BuildContext context, String routeName) {
    Navigator.pushNamed(context, routeName);
  }

  // Replace current screen with a named route (The "Seamless" way)
  static void replaceWith(BuildContext context, String routeName) {
    Navigator.pushReplacementNamed(context, routeName);
  }

  // Keep these just in case you need to pass a specific Widget manually
  static void pushWidget(BuildContext context, Widget screen) {
    Navigator.push(context, MaterialPageRoute(builder: (context) => screen));
  }
}
