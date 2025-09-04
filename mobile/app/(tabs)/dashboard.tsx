import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  ScrollView,
  Alert,
} from 'react-native';
import { useBudgetStore } from '../../stores/budgetStore';
import BudgetChart from '../../components/BudgetChart';

export default function Dashboard() {
  const [budgetAmount, setBudgetAmount] = useState('');
  const [duration, setDuration] = useState<'daily' | 'weekly' | 'monthly'>('monthly');
  
  const { 
    currentBudget, 
    breakdown, 
    isLoading, 
    calculateBudget,
    getSavingsForecast,
    getInsights 
  } = useBudgetStore();

  // Debug: Log state changes
  console.log('Dashboard render - breakdown:', breakdown);
  console.log('Dashboard render - budgetAmount:', budgetAmount);
  console.log('Dashboard render - isLoading:', isLoading);
  console.log('Dashboard render - currentBudget:', currentBudget);

  const handleCalculate = async () => {
    console.log('handleCalculate called');
    if (!budgetAmount || parseFloat(budgetAmount) <= 0) {
      Alert.alert('Error', 'Please enter a valid budget amount');
      return;
    }

    try {
      console.log('About to calculate budget:', budgetAmount, duration);
      
      // Calculate budget breakdown
      await calculateBudget(parseFloat(budgetAmount), duration);
      console.log('Budget calculated, breakdown:', breakdown);
      
    } catch (error) {
      Alert.alert('Error', 'Failed to calculate budget. Please try again.');
      console.error('Budget calculation error:', error);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-PH', {
      style: 'currency',
      currency: 'PHP',
      minimumFractionDigits: 2,
    }).format(amount);
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.inputSection}>
        <Text style={styles.title}>Budget Calculator</Text>
        
        <View style={styles.inputGroup}>
          <Text style={styles.label}>Budget Amount</Text>
          <TextInput
            style={styles.input}
            value={budgetAmount}
            onChangeText={setBudgetAmount}
            placeholder="Enter amount (e.g., 10000)"
            keyboardType="numeric"
          />
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Duration</Text>
          <View style={styles.durationButtons}>
            {(['daily', 'weekly', 'monthly'] as const).map((option) => (
              <TouchableOpacity
                key={option}
                style={[
                  styles.durationButton,
                  duration === option && styles.durationButtonActive
                ]}
                onPress={() => setDuration(option)}
              >
                <Text style={[
                  styles.durationButtonText,
                  duration === option && styles.durationButtonTextActive
                ]}>
                  {option.charAt(0).toUpperCase() + option.slice(1)}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        <TouchableOpacity
          style={[styles.calculateButton, isLoading && styles.calculateButtonDisabled]}
          onPress={handleCalculate}
          disabled={isLoading}
        >
          <Text style={styles.calculateButtonText}>
            {isLoading ? 'Calculating...' : 'Calculate Budget'}
          </Text>
        </TouchableOpacity>
      </View>

      {breakdown && (
        <View style={styles.resultsSection}>
          <Text style={styles.sectionTitle}>Budget Breakdown</Text>
          
          {/* Budget Chart */}
          <BudgetChart breakdown={breakdown} />
          
          {/* Categories List */}
          <View style={styles.categoriesList}>
            {Object.entries(breakdown.categories).map(([category, amount]) => (
              <View key={category} style={styles.categoryItem}>
                <Text style={styles.categoryName}>
                  {category.charAt(0).toUpperCase() + category.slice(1).replace('_', ' ')}
                </Text>
                <Text style={styles.categoryAmount}>
                  {formatCurrency(amount)}
                </Text>
              </View>
            ))}
          </View>

          <View style={styles.totalSection}>
            <View style={styles.totalItem}>
              <Text style={styles.totalLabel}>Essential Expenses</Text>
              <Text style={styles.totalAmount}>
                {formatCurrency(breakdown.total_essential)}
              </Text>
            </View>
            <View style={styles.totalItem}>
              <Text style={styles.totalLabel}>Total Savings</Text>
              <Text style={[styles.totalAmount, styles.savingsAmount]}>
                {formatCurrency(breakdown.total_savings)}
              </Text>
            </View>
          </View>
          
          {/* Debug Information */}
          <View style={styles.debugSection}>
            <Text style={styles.debugText}>
              Debug: Categories: {Object.keys(breakdown.categories).length}
              {'\n'}Essential: ₱{breakdown.total_essential}
              {'\n'}Savings: ₱{breakdown.total_savings}
              {'\n'}JSON: {JSON.stringify(breakdown, null, 2).substring(0, 200)}...
            </Text>
          </View>
        </View>
      )}
      
      {!breakdown && !isLoading && (
        <View style={styles.noDataSection}>
          <Text style={styles.noDataText}>
            💡 Enter a budget amount and tap "Calculate Budget" to see your breakdown
          </Text>
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  inputSection: {
    backgroundColor: 'white',
    padding: 20,
    margin: 16,
    borderRadius: 12,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
    textAlign: 'center',
    color: '#333',
  },
  inputGroup: {
    marginBottom: 20,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
    color: '#333',
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    backgroundColor: '#fafafa',
  },
  durationButtons: {
    flexDirection: 'row',
    gap: 8,
  },
  durationButton: {
    flex: 1,
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#ddd',
    alignItems: 'center',
  },
  durationButtonActive: {
    backgroundColor: '#2196F3',
    borderColor: '#2196F3',
  },
  durationButtonText: {
    fontSize: 14,
    color: '#666',
  },
  durationButtonTextActive: {
    color: 'white',
    fontWeight: '600',
  },
  calculateButton: {
    backgroundColor: '#2196F3',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  calculateButtonDisabled: {
    opacity: 0.6,
  },
  calculateButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  resultsSection: {
    backgroundColor: 'white',
    margin: 16,
    marginTop: 0,
    padding: 20,
    borderRadius: 12,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 16,
    color: '#333',
  },
  categoriesList: {
    marginTop: 16,
  },
  categoryItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  categoryName: {
    fontSize: 16,
    color: '#333',
  },
  categoryAmount: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2196F3',
  },
  totalSection: {
    marginTop: 16,
    paddingTop: 16,
    borderTopWidth: 2,
    borderTopColor: '#f0f0f0',
  },
  totalItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
  },
  totalLabel: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
  },
  totalAmount: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  savingsAmount: {
    color: '#4CAF50',
  },
  debugSection: {
    marginTop: 16,
    padding: 12,
    backgroundColor: '#f8f8f8',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#ddd',
  },
  debugText: {
    fontSize: 12,
    color: '#666',
    fontFamily: 'monospace',
  },
  noDataSection: {
    backgroundColor: 'white',
    margin: 16,
    padding: 40,
    borderRadius: 12,
    alignItems: 'center',
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  noDataText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    lineHeight: 24,
  },
});
