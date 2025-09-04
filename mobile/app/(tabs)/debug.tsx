import React from 'react';
import { View, Text, StyleSheet, SafeAreaView } from 'react-native';

export default function DebugDashboard() {
  console.log('🔥 DebugDashboard rendering...');
  
  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.container}>
        <Text style={styles.title}>✅ DEBUG WORKS!</Text>
        <Text style={styles.text}>Mobile Connection: SUCCESS</Text>
        <Text style={styles.text}>Budget Buddy v2.0</Text>
        <Text style={styles.text}>Port: 8083</Text>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
    color: '#333',
  },
  text: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 10,
  },
});
