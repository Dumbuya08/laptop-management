import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class DashboardScreen extends StatelessWidget {
  Future<List> fetchLaptops() async {
    final response = await http.get(Uri.parse('http://localhost:5000/dashboard'));
    if (response.statusCode == 200) {
      return List.from(json.decode(response.body));
    } else {
      throw Exception('Failed to load laptops');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Laptop Management Dashboard')),
      body: FutureBuilder<List>(
        future: fetchLaptops(),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return Center(child: CircularProgressIndicator());
          } else if (snapshot.hasError) {
            return Center(child: Text('Error: ${snapshot.error}'));
          } else {
            final laptops = snapshot.data!;
            return ListView.builder(
              itemCount: laptops.length,
              itemBuilder: (context, index) {
                return ListTile(
                  title: Text(laptops[index]['serial_number']),
                  subtitle: Text(laptops[index]['model']),
                );
              },
            );
          }
        },
      ),
    );
  }
}
