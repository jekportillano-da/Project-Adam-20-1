import { Tabs } from 'expo-router';
import React from 'react';
import { Text } from 'react-native';

export default function TabLayout() {
  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: '#2196F3',
        headerStyle: {
          backgroundColor: '#2196F3',
        },
        headerShadowVisible: false,
        headerTintColor: '#fff',
        tabBarStyle: {
          backgroundColor: '#fff',
        },
      }}
    >
      <Tabs.Screen
        name="debug"
        options={{
          title: 'Debug',
          tabBarIcon: ({ color, focused }) => (
            <TabIcon name={focused ? 'bug' : 'bug-outline'} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="dashboard"
        options={{
          title: 'Dashboard',
          tabBarIcon: ({ color, focused }) => (
            <TabIcon name={focused ? 'home' : 'home-outline'} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="insights"
        options={{
          title: 'Insights',
          tabBarIcon: ({ color, focused }) => (
            <TabIcon name={focused ? 'analytics' : 'analytics-outline'} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="settings"
        options={{
          title: 'Settings',
          tabBarIcon: ({ color, focused }) => (
            <TabIcon name={focused ? 'settings' : 'settings-outline'} color={color} />
          ),
        }}
      />
    </Tabs>
  );
}

// Simple icon component - replace with proper icons later
function TabIcon({ name, color }: { name: string; color: string }) {
  const getEmoji = () => {
    if (name === 'bug' || name === 'bug-outline') return '🐛';
    if (name === 'home' || name === 'home-outline') return '🏠';
    if (name === 'analytics' || name === 'analytics-outline') return '📊';
    return '⚙️';
  };
  
  return <Text style={{ color, fontSize: 20 }}>{getEmoji()}</Text>;
}
