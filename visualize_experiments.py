"""
Visualization Script for LLM Mobile QA Experiments
Generates comprehensive plots for Phase 1 and Phase 2 results
"""

import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json

# Set style
sns.set_style("whitegrid")
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10


class ExperimentVisualizer:
    """Generate visualizations from experiment database"""
    
    def __init__(self, db_path: str = 'experiments.db'):
        self.db_path = db_path
        self.df = self.load_data()
        
    def load_data(self) -> pd.DataFrame:
        """Load experiment data from database"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM experiments", conn)
        conn.close()
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        return df
    
    def save_plot(self, filename: str, dpi: int = 300):
        """Save current plot to file"""
        output_dir = Path('experiment_results')
        output_dir.mkdir(exist_ok=True)
        plt.savefig(output_dir / filename, dpi=dpi, bbox_inches='tight')
        print(f"✅ Saved: {output_dir / filename}")
    
    # ========== PHASE 1.1 VISUALIZATIONS ==========
    
    def plot_phase1_1_success_rates(self):
        """Plot success rates for each test (Experiment 1.1)"""
        phase1_1 = self.df[self.df['experiment_id'].str.contains('phase1_exp1.1')]
        
        if len(phase1_1) == 0:
            print("⚠️ No Phase 1.1 data found")
            return
        
        # Calculate success rates by test
        success_rates = phase1_1.groupby('test_id')['success'].agg(['mean', 'count', 'std']).reset_index()
        success_rates['mean'] = success_rates['mean'] * 100
        success_rates['std'] = success_rates['std'] * 100
        success_rates['ci'] = 1.96 * success_rates['std'] / np.sqrt(success_rates['count'])
        
        # Create plot
        fig, ax = plt.subplots(figsize=(10, 6))
        
        x = np.arange(len(success_rates))
        bars = ax.bar(x, success_rates['mean'], yerr=success_rates['ci'],
                      capsize=5, alpha=0.7, edgecolor='black', linewidth=1.5)
        
        # Color bars based on success rate
        colors = ['#2ecc71' if rate >= 80 else '#e74c3c' if rate < 50 else '#f39c12' 
                  for rate in success_rates['mean']]
        for bar, color in zip(bars, colors):
            bar.set_color(color)
        
        ax.set_xlabel('Test ID', fontsize=12, fontweight='bold')
        ax.set_ylabel('Success Rate (%)', fontsize=12, fontweight='bold')
        ax.set_title('Phase 1.1: Baseline Success Rates by Test\n(with 95% Confidence Intervals)', 
                     fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(success_rates['test_id'])
        ax.set_ylim([0, 105])
        ax.axhline(y=80, color='gray', linestyle='--', alpha=0.5, label='80% Target')
        
        # Add value labels on bars
        for i, (idx, row) in enumerate(success_rates.iterrows()):
            ax.text(i, row['mean'] + row['ci'] + 2, f"{row['mean']:.1f}%",
                   ha='center', va='bottom', fontweight='bold')
        
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        self.save_plot('phase1_1_success_rates.png')
        plt.show()
    
    def plot_phase1_1_execution_times(self):
        """Plot execution time distributions (Experiment 1.1)"""
        phase1_1 = self.df[self.df['experiment_id'].str.contains('phase1_exp1.1')]
        
        if len(phase1_1) == 0:
            print("⚠️ No Phase 1.1 data found")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        test_ids = phase1_1['test_id'].unique()
        
        for idx, test_id in enumerate(sorted(test_ids)[:4]):
            ax = axes[idx // 2, idx % 2]
            test_data = phase1_1[phase1_1['test_id'] == test_id]
            
            # Violin plot with box plot overlay
            parts = ax.violinplot([test_data['execution_time_seconds']], 
                                  positions=[0], widths=0.7, showmeans=True)
            
            for pc in parts['bodies']:
                pc.set_facecolor('#3498db')
                pc.set_alpha(0.6)
            
            # Box plot overlay
            bp = ax.boxplot([test_data['execution_time_seconds']], 
                           positions=[0], widths=0.3, patch_artist=True)
            for patch in bp['boxes']:
                patch.set_facecolor('white')
                patch.set_alpha(0.7)
            
            # Statistics
            mean_time = test_data['execution_time_seconds'].mean()
            median_time = test_data['execution_time_seconds'].median()
            std_time = test_data['execution_time_seconds'].std()
            
            ax.set_title(f'{test_id.upper()}\n'
                        f'Mean: {mean_time:.1f}s | Median: {median_time:.1f}s | Std: {std_time:.1f}s',
                        fontsize=11, fontweight='bold')
            ax.set_ylabel('Execution Time (seconds)', fontsize=10)
            ax.set_xticks([])
            ax.grid(axis='y', alpha=0.3)
        
        plt.suptitle('Phase 1.1: Execution Time Distributions', 
                     fontsize=14, fontweight='bold', y=1.00)
        plt.tight_layout()
        self.save_plot('phase1_1_execution_times.png')
        plt.show()
    
    def plot_phase1_1_cost_analysis(self):
        """Plot cost analysis (Experiment 1.1)"""
        phase1_1 = self.df[self.df['experiment_id'].str.contains('phase1_exp1.1')]
        
        if len(phase1_1) == 0:
            print("⚠️ No Phase 1.1 data found")
            return
        
        # Aggregate by test
        cost_data = phase1_1.groupby('test_id').agg({
            'estimated_cost_usd': ['sum', 'mean'],
            'total_tokens_used': ['sum', 'mean'],
            'api_calls_made': ['sum', 'mean']
        }).reset_index()
        
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        # Total cost per test
        ax = axes[0]
        x = np.arange(len(cost_data))
        bars = ax.bar(x, cost_data[('estimated_cost_usd', 'sum')], alpha=0.7, edgecolor='black')
        ax.set_xlabel('Test ID', fontweight='bold')
        ax.set_ylabel('Total Cost (USD)', fontweight='bold')
        ax.set_title('Total Cost per Test Suite', fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(cost_data['test_id'])
        
        for i, v in enumerate(cost_data[('estimated_cost_usd', 'sum')]):
            ax.text(i, v, f'${v:.4f}', ha='center', va='bottom', fontweight='bold')
        
        # Average tokens per test
        ax = axes[1]
        bars = ax.bar(x, cost_data[('total_tokens_used', 'mean')], 
                     color='#e74c3c', alpha=0.7, edgecolor='black')
        ax.set_xlabel('Test ID', fontweight='bold')
        ax.set_ylabel('Avg Tokens per Run', fontweight='bold')
        ax.set_title('Average Token Usage', fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(cost_data['test_id'])
        
        for i, v in enumerate(cost_data[('total_tokens_used', 'mean')]):
            ax.text(i, v, f'{int(v)}', ha='center', va='bottom', fontweight='bold')
        
        # Average API calls
        ax = axes[2]
        bars = ax.bar(x, cost_data[('api_calls_made', 'mean')], 
                     color='#2ecc71', alpha=0.7, edgecolor='black')
        ax.set_xlabel('Test ID', fontweight='bold')
        ax.set_ylabel('Avg API Calls per Run', fontweight='bold')
        ax.set_title('Average API Call Count', fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(cost_data['test_id'])
        
        for i, v in enumerate(cost_data[('api_calls_made', 'mean')]):
            ax.text(i, v, f'{int(v)}', ha='center', va='bottom', fontweight='bold')
        
        plt.suptitle('Phase 1.1: Cost and Resource Analysis', fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        self.save_plot('phase1_1_cost_analysis.png')
        plt.show()
    
    def plot_phase1_1_failure_modes(self):
        """Plot failure mode distribution (Experiment 1.1)"""
        phase1_1 = self.df[self.df['experiment_id'].str.contains('phase1_exp1.1')]
        failures = phase1_1[phase1_1['success'] == False]
        
        if len(failures) == 0:
            print("✅ No failures in Phase 1.1 - Perfect success rate!")
            return
        
        # Count failure modes
        failure_counts = failures['failure_mode'].value_counts()
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Pie chart
        colors = ['#e74c3c', '#f39c12', '#9b59b6', '#3498db', '#2ecc71']
        wedges, texts, autotexts = ax1.pie(failure_counts.values, 
                                           labels=failure_counts.index,
                                           autopct='%1.1f%%',
                                           colors=colors,
                                           startangle=90)
        ax1.set_title('Failure Mode Distribution', fontweight='bold', fontsize=12)
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        # Bar chart by test
        failure_by_test = failures.groupby(['test_id', 'failure_mode']).size().unstack(fill_value=0)
        failure_by_test.plot(kind='bar', stacked=True, ax=ax2, color=colors, alpha=0.8)
        ax2.set_xlabel('Test ID', fontweight='bold')
        ax2.set_ylabel('Number of Failures', fontweight='bold')
        ax2.set_title('Failures by Test and Mode', fontweight='bold', fontsize=12)
        ax2.legend(title='Failure Mode', bbox_to_anchor=(1.05, 1), loc='upper left')
        ax2.grid(axis='y', alpha=0.3)
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=0)
        
        plt.suptitle('Phase 1.1: Failure Analysis', fontsize=14, fontweight='bold', y=1.00)
        plt.tight_layout()
        self.save_plot('phase1_1_failure_modes.png')
        plt.show()
    
    # ========== PHASE 1.2 VISUALIZATIONS ==========
    
    def plot_phase1_2_temperature_effect(self):
        """Plot effect of temperature on success rate (Experiment 1.2a)"""
        temp_data = self.df[self.df['experiment_id'].str.contains('phase1_exp1.2a')]
        
        if len(temp_data) == 0:
            print("⚠️ No Phase 1.2a temperature data found")
            return
        
        # Group by temperature
        temp_results = temp_data.groupby('temperature').agg({
            'success': ['mean', 'std', 'count'],
            'execution_time_seconds': 'mean',
            'estimated_cost_usd': 'mean'
        }).reset_index()
        
        temp_results.columns = ['temperature', 'success_mean', 'success_std', 'count',
                               'time_mean', 'cost_mean']
        temp_results['success_mean'] *= 100
        temp_results['success_std'] *= 100
        temp_results['ci'] = 1.96 * temp_results['success_std'] / np.sqrt(temp_results['count'])
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Success rate vs temperature
        ax1.errorbar(temp_results['temperature'], temp_results['success_mean'],
                    yerr=temp_results['ci'], marker='o', markersize=10,
                    capsize=5, linewidth=2, color='#3498db')
        ax1.fill_between(temp_results['temperature'],
                        temp_results['success_mean'] - temp_results['ci'],
                        temp_results['success_mean'] + temp_results['ci'],
                        alpha=0.2, color='#3498db')
        ax1.set_xlabel('Temperature', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Success Rate (%)', fontsize=12, fontweight='bold')
        ax1.set_title('Success Rate vs Temperature', fontsize=12, fontweight='bold')
        ax1.grid(alpha=0.3)
        ax1.axhline(y=80, color='gray', linestyle='--', alpha=0.5, label='80% Target')
        ax1.legend()
        
        # Execution time vs temperature
        ax2.plot(temp_results['temperature'], temp_results['time_mean'],
                marker='s', markersize=10, linewidth=2, color='#e74c3c')
        ax2.set_xlabel('Temperature', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Avg Execution Time (s)', fontsize=12, fontweight='bold')
        ax2.set_title('Execution Time vs Temperature', fontsize=12, fontweight='bold')
        ax2.grid(alpha=0.3)
        
        plt.suptitle('Phase 1.2a: Temperature Effect Analysis', fontsize=14, fontweight='bold')
        plt.tight_layout()
        self.save_plot('phase1_2_temperature_effect.png')
        plt.show()
    
    def plot_phase1_2_context_effect(self):
        """Plot effect of context window size (Experiment 1.2b)"""
        context_data = self.df[self.df['experiment_id'].str.contains('phase1_exp1.2b')]
        
        if len(context_data) == 0:
            print("⚠️ No Phase 1.2b context data found")
            return
        
        # Group by context window size
        context_results = context_data.groupby('context_window_size').agg({
            'success': ['mean', 'std', 'count'],
            'execution_time_seconds': 'mean',
            'total_tokens_used': 'mean'
        }).reset_index()
        
        context_results.columns = ['context_size', 'success_mean', 'success_std', 'count',
                                   'time_mean', 'tokens_mean']
        context_results['success_mean'] *= 100
        context_results['success_std'] *= 100
        context_results['ci'] = 1.96 * context_results['success_std'] / np.sqrt(context_results['count'])
        
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        x = np.arange(len(context_results))
        
        # Success rate
        ax = axes[0]
        bars = ax.bar(x, context_results['success_mean'], yerr=context_results['ci'],
                     capsize=5, alpha=0.7, edgecolor='black', color='#3498db')
        ax.set_xlabel('Context Window Size', fontweight='bold')
        ax.set_ylabel('Success Rate (%)', fontweight='bold')
        ax.set_title('Success vs Context Size', fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(context_results['context_size'])
        ax.axhline(y=80, color='gray', linestyle='--', alpha=0.5)
        
        for i, v in enumerate(context_results['success_mean']):
            ax.text(i, v + context_results['ci'].iloc[i] + 2, f'{v:.1f}%',
                   ha='center', va='bottom', fontweight='bold')
        
        # Execution time
        ax = axes[1]
        ax.bar(x, context_results['time_mean'], alpha=0.7, 
               edgecolor='black', color='#e74c3c')
        ax.set_xlabel('Context Window Size', fontweight='bold')
        ax.set_ylabel('Avg Execution Time (s)', fontweight='bold')
        ax.set_title('Time vs Context Size', fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(context_results['context_size'])
        
        # Token usage
        ax = axes[2]
        ax.bar(x, context_results['tokens_mean'], alpha=0.7,
               edgecolor='black', color='#2ecc71')
        ax.set_xlabel('Context Window Size', fontweight='bold')
        ax.set_ylabel('Avg Tokens Used', fontweight='bold')
        ax.set_title('Tokens vs Context Size', fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(context_results['context_size'])
        
        plt.suptitle('Phase 1.2b: Context Window Size Effect', fontsize=14, fontweight='bold')
        plt.tight_layout()
        self.save_plot('phase1_2_context_effect.png')
        plt.show()
    
    def plot_phase1_2_fewshot_effect(self):
        """Plot effect of few-shot examples (Experiment 1.2c)"""
        fewshot_data = self.df[self.df['experiment_id'].str.contains('phase1_exp1.2c')]
        
        if len(fewshot_data) == 0:
            print("⚠️ No Phase 1.2c few-shot data found")
            return
        
        # Group by few-shot count
        fewshot_results = fewshot_data.groupby('few_shot_examples').agg({
            'success': ['mean', 'std', 'count'],
            'execution_time_seconds': 'mean'
        }).reset_index()
        
        fewshot_results.columns = ['fewshot_count', 'success_mean', 'success_std', 
                                   'count', 'time_mean']
        fewshot_results['success_mean'] *= 100
        fewshot_results['success_std'] *= 100
        fewshot_results['ci'] = 1.96 * fewshot_results['success_std'] / np.sqrt(fewshot_results['count'])
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        x = np.arange(len(fewshot_results))
        
        # Success rate
        bars = ax1.bar(x, fewshot_results['success_mean'], yerr=fewshot_results['ci'],
                      capsize=5, alpha=0.7, edgecolor='black')
        
        colors = ['#e74c3c', '#f39c12', '#2ecc71']
        for bar, color in zip(bars, colors):
            bar.set_color(color)
        
        ax1.set_xlabel('Number of Few-Shot Examples', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Success Rate (%)', fontsize=12, fontweight='bold')
        ax1.set_title('Success Rate vs Few-Shot Examples', fontsize=12, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(fewshot_results['fewshot_count'])
        ax1.axhline(y=80, color='gray', linestyle='--', alpha=0.5)
        
        for i, v in enumerate(fewshot_results['success_mean']):
            ax1.text(i, v + fewshot_results['ci'].iloc[i] + 2, f'{v:.1f}%',
                    ha='center', va='bottom', fontweight='bold')
        
        # Improvement over baseline
        baseline = fewshot_results[fewshot_results['fewshot_count'] == 0]['success_mean'].values[0]
        improvements = fewshot_results['success_mean'] - baseline
        
        ax2.bar(x, improvements, alpha=0.7, edgecolor='black', color=colors)
        ax2.set_xlabel('Number of Few-Shot Examples', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Improvement over Baseline (%)', fontsize=12, fontweight='bold')
        ax2.set_title('Success Rate Improvement', fontsize=12, fontweight='bold')
        ax2.set_xticks(x)
        ax2.set_xticklabels(fewshot_results['fewshot_count'])
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
        
        for i, v in enumerate(improvements):
            y_pos = v + 1 if v > 0 else v - 1
            ax2.text(i, y_pos, f'{v:+.1f}%', ha='center', 
                    va='bottom' if v > 0 else 'top', fontweight='bold')
        
        plt.suptitle('Phase 1.2c: Few-Shot Example Effect', fontsize=14, fontweight='bold')
        plt.tight_layout()
        self.save_plot('phase1_2_fewshot_effect.png')
        plt.show()
    
    def plot_phase1_2_constraint_effect(self):
        """Plot effect of constraint levels (Experiment 1.2d)"""
        constraint_data = self.df[self.df['experiment_id'].str.contains('phase1_exp1.2d')]
        
        if len(constraint_data) == 0:
            print("⚠️ No Phase 1.2d constraint data found")
            return
        
        # Group by constraint level
        constraint_results = constraint_data.groupby('constraint_level').agg({
            'success': ['mean', 'std', 'count'],
            'execution_time_seconds': 'mean',
            'supervisor_interventions': 'mean'
        }).reset_index()
        
        constraint_results.columns = ['constraint_level', 'success_mean', 'success_std',
                                      'count', 'time_mean', 'interventions_mean']
        constraint_results['success_mean'] *= 100
        constraint_results['success_std'] *= 100
        constraint_results['ci'] = 1.96 * constraint_results['success_std'] / np.sqrt(constraint_results['count'])
        
        # Order: loose, moderate, strict
        order = ['loose', 'moderate', 'strict']
        constraint_results = constraint_results.set_index('constraint_level').reindex(order).reset_index()
        
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        x = np.arange(len(constraint_results))
        
        # Success rate
        ax = axes[0]
        bars = ax.bar(x, constraint_results['success_mean'], yerr=constraint_results['ci'],
                     capsize=5, alpha=0.7, edgecolor='black')
        colors = ['#e74c3c', '#f39c12', '#2ecc71']
        for bar, color in zip(bars, colors):
            bar.set_color(color)
        
        ax.set_xlabel('Constraint Level', fontweight='bold')
        ax.set_ylabel('Success Rate (%)', fontweight='bold')
        ax.set_title('Success vs Constraint Level', fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(constraint_results['constraint_level'])
        ax.axhline(y=80, color='gray', linestyle='--', alpha=0.5)
        
        for i, v in enumerate(constraint_results['success_mean']):
            ax.text(i, v + constraint_results['ci'].iloc[i] + 2, f'{v:.1f}%',
                   ha='center', va='bottom', fontweight='bold')
        
        # Execution time
        ax = axes[1]
        ax.bar(x, constraint_results['time_mean'], alpha=0.7, 
               edgecolor='black', color=colors)
        ax.set_xlabel('Constraint Level', fontweight='bold')
        ax.set_ylabel('Avg Execution Time (s)', fontweight='bold')
        ax.set_title('Time vs Constraint Level', fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(constraint_results['constraint_level'])
        
        # Supervisor interventions
        ax = axes[2]
        ax.bar(x, constraint_results['interventions_mean'], alpha=0.7,
               edgecolor='black', color=colors)
        ax.set_xlabel('Constraint Level', fontweight='bold')
        ax.set_ylabel('Avg Interventions', fontweight='bold')
        ax.set_title('Interventions vs Constraint Level', fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(constraint_results['constraint_level'])
        
        plt.suptitle('Phase 1.2d: Constraint Level Effect', fontsize=14, fontweight='bold')
        plt.tight_layout()
        self.save_plot('phase1_2_constraint_effect.png')
        plt.show()
    
    def plot_phase1_2_heatmap(self):
        """Heatmap of all Phase 1.2 variations"""
        phase1_2 = self.df[self.df['experiment_id'].str.contains('phase1_exp1.2')]
        
        if len(phase1_2) == 0:
            print("⚠️ No Phase 1.2 data found")
            return
        
        # Create a summary matrix
        variations = []
        
        # Temperature
        for temp in [0.1, 0.3, 0.5, 0.7, 0.9]:
            data = phase1_2[phase1_2['temperature'] == temp]
            if len(data) > 0:
                variations.append({
                    'Category': 'Temperature',
                    'Value': str(temp),
                    'Success Rate': data['success'].mean() * 100,
                    'Avg Time': data['execution_time_seconds'].mean(),
                    'N': len(data)
                })
        
        # Context
        for size in [3, 5, 10]:
            data = phase1_2[phase1_2['context_window_size'] == size]
            if len(data) > 0:
                variations.append({
                    'Category': 'Context Size',
                    'Value': str(size),
                    'Success Rate': data['success'].mean() * 100,
                    'Avg Time': data['execution_time_seconds'].mean(),
                    'N': len(data)
                })
        
        # Few-shot
        for count in [0, 2, 5]:
            data = phase1_2[phase1_2['few_shot_examples'] == count]
            if len(data) > 0:
                variations.append({
                    'Category': 'Few-Shot',
                    'Value': str(count),
                    'Success Rate': data['success'].mean() * 100,
                    'Avg Time': data['execution_time_seconds'].mean(),
                    'N': len(data)
                })
        
        # Constraint
        for level in ['loose', 'moderate', 'strict']:
            data = phase1_2[phase1_2['constraint_level'] == level]
            if len(data) > 0:
                variations.append({
                    'Category': 'Constraint',
                    'Value': level,
                    'Success Rate': data['success'].mean() * 100,
                    'Avg Time': data['execution_time_seconds'].mean(),
                    'N': len(data)
                })
        
        df_variations = pd.DataFrame(variations)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 8))
        
        # Success rate heatmap
        pivot_success = df_variations.pivot(index='Value', columns='Category', values='Success Rate')
        sns.heatmap(pivot_success, annot=True, fmt='.1f', cmap='RdYlGn', 
                   vmin=0, vmax=100, ax=ax1, cbar_kws={'label': 'Success Rate (%)'})
        ax1.set_title('Success Rate by Variation', fontweight='bold', fontsize=12)
        ax1.set_xlabel('')
        ax1.set_ylabel('Parameter Value', fontweight='bold')
        
        # Execution time heatmap
        pivot_time = df_variations.pivot(index='Value', columns='Category', values='Avg Time')
        sns.heatmap(pivot_time, annot=True, fmt='.1f', cmap='YlOrRd',
                   ax=ax2, cbar_kws={'label': 'Avg Time (s)'})
        ax2.set_title('Execution Time by Variation', fontweight='bold', fontsize=12)
        ax2.set_xlabel('')
        ax2.set_ylabel('Parameter Value', fontweight='bold')
        
        plt.suptitle('Phase 1.2: Comprehensive Prompt Variation Heatmap', 
                     fontsize=14, fontweight='bold')
        plt.tight_layout()
        self.save_plot('phase1_2_heatmap.png')
        plt.show()
    
    # ========== PHASE 2.1 VISUALIZATIONS ==========
    
    def plot_phase2_1_model_comparison(self):
        """Comprehensive model comparison (Experiment 2.1)"""
        phase2_1 = self.df[self.df['experiment_id'].str.contains('phase2_exp2.1')]
        
        if len(phase2_1) == 0:
            print("⚠️ No Phase 2.1 data found")
            return
        
        # Overall model performance
        model_results = phase2_1.groupby('model').agg({
            'success': ['mean', 'std', 'count'],
            'execution_time_seconds': 'mean',
            'estimated_cost_usd': 'mean',
            'total_tokens_used': 'mean'
        }).reset_index()
        
        model_results.columns = ['model', 'success_mean', 'success_std', 'count',
                                'time_mean', 'cost_mean', 'tokens_mean']
        model_results['success_mean'] *= 100
        model_results['success_std'] *= 100
        model_results['ci'] = 1.96 * model_results['success_std'] / np.sqrt(model_results['count'])
        
        fig = plt.figure(figsize=(16, 10))
        gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
        
        # 1. Overall success rate comparison
        ax1 = fig.add_subplot(gs[0, :])
        x = np.arange(len(model_results))
        bars = ax1.bar(x, model_results['success_mean'], yerr=model_results['ci'],
                      capsize=5, alpha=0.7, edgecolor='black', linewidth=1.5)
        
        # Color based on performance
        colors = ['#2ecc71' if rate >= 80 else '#e74c3c' if rate < 50 else '#f39c12' 
                  for rate in model_results['success_mean']]
        for bar, color in zip(bars, colors):
            bar.set_color(color)
        
        ax1.set_xlabel('Model', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Success Rate (%)', fontsize=12, fontweight='bold')
        ax1.set_title('Overall Success Rate by Model (with 95% CI)', fontsize=13, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(model_results['model'], rotation=15, ha='right')
        ax1.set_ylim([0, 105])
        ax1.axhline(y=80, color='gray', linestyle='--', alpha=0.5, label='80% Target')
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)
        
        for i, (idx, row) in enumerate(model_results.iterrows()):
            ax1.text(i, row['success_mean'] + row['ci'] + 2, f"{row['success_mean']:.1f}%",
                    ha='center', va='bottom', fontweight='bold', fontsize=10)
        
        # 2. Success by test and model
        ax2 = fig.add_subplot(gs[1, 0])
        test_model_success = phase2_1.groupby(['test_id', 'model'])['success'].mean().unstack() * 100
        test_model_success.plot(kind='bar', ax=ax2, alpha=0.8)
        ax2.set_xlabel('Test ID', fontweight='bold')
        ax2.set_ylabel('Success Rate (%)', fontweight='bold')
        ax2.set_title('Success Rate by Test and Model', fontweight='bold')
        ax2.legend(title='Model', bbox_to_anchor=(1.05, 1), loc='upper left')
        ax2.grid(axis='y', alpha=0.3)
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=0)
        
        # 3. Execution time comparison
        ax3 = fig.add_subplot(gs[1, 1])
        x = np.arange(len(model_results))
        ax3.bar(x, model_results['time_mean'], alpha=0.7, 
               color='#3498db', edgecolor='black')
        ax3.set_xlabel('Model', fontweight='bold')
        ax3.set_ylabel('Avg Execution Time (s)', fontweight='bold')
        ax3.set_title('Average Execution Time', fontweight='bold')
        ax3.set_xticks(x)
        ax3.set_xticklabels(model_results['model'], rotation=15, ha='right')
        ax3.grid(axis='y', alpha=0.3)
        
        for i, v in enumerate(model_results['time_mean']):
            ax3.text(i, v, f'{v:.1f}s', ha='center', va='bottom', fontweight='bold')
        
        # 4. Cost comparison
        ax4 = fig.add_subplot(gs[2, 0])
        ax4.bar(x, model_results['cost_mean'], alpha=0.7,
               color='#e74c3c', edgecolor='black')
        ax4.set_xlabel('Model', fontweight='bold')
        ax4.set_ylabel('Avg Cost per Run (USD)', fontweight='bold')
        ax4.set_title('Average Cost per Test Run', fontweight='bold')
        ax4.set_xticks(x)
        ax4.set_xticklabels(model_results['model'], rotation=15, ha='right')
        ax4.grid(axis='y', alpha=0.3)
        
        for i, v in enumerate(model_results['cost_mean']):
            ax4.text(i, v, f'${v:.5f}', ha='center', va='bottom', fontweight='bold', fontsize=9)
        
        # 5. Cost-Quality tradeoff scatter
        ax5 = fig.add_subplot(gs[2, 1])
        scatter = ax5.scatter(model_results['cost_mean'], model_results['success_mean'],
                             s=model_results['tokens_mean']/10, alpha=0.6,
                             c=range(len(model_results)), cmap='viridis')
        
        for i, row in model_results.iterrows():
            ax5.annotate(row['model'], (row['cost_mean'], row['success_mean']),
                        xytext=(5, 5), textcoords='offset points', fontsize=9)
        
        ax5.set_xlabel('Avg Cost per Run (USD)', fontweight='bold')
        ax5.set_ylabel('Success Rate (%)', fontweight='bold')
        ax5.set_title('Cost-Quality Tradeoff (bubble size = tokens)', fontweight='bold')
        ax5.grid(alpha=0.3)
        ax5.axhline(y=80, color='gray', linestyle='--', alpha=0.5)
        
        plt.suptitle('Phase 2.1: Comprehensive Model Comparison', 
                     fontsize=16, fontweight='bold')
        self.save_plot('phase2_1_model_comparison.png')
        plt.show()
    
    def plot_phase2_1_radar_chart(self):
        """Radar chart for multi-metric model comparison"""
        phase2_1 = self.df[self.df['experiment_id'].str.contains('phase2_exp2.1')]
        
        if len(phase2_1) == 0:
            print("⚠️ No Phase 2.1 data found")
            return
        
        # Calculate normalized metrics
        model_metrics = phase2_1.groupby('model').agg({
            'success': 'mean',
            'execution_time_seconds': 'mean',
            'estimated_cost_usd': 'mean',
            'supervisor_interventions': 'mean'
        }).reset_index()
        
        # Normalize to 0-100 scale
        model_metrics['success_norm'] = model_metrics['success'] * 100
        
        # Invert time and cost (lower is better)
        max_time = model_metrics['execution_time_seconds'].max()
        model_metrics['speed_norm'] = (1 - model_metrics['execution_time_seconds'] / max_time) * 100
        
        max_cost = model_metrics['estimated_cost_usd'].max()
        model_metrics['cost_eff_norm'] = (1 - model_metrics['estimated_cost_usd'] / max_cost) * 100
        
        # Invert interventions (fewer is better)
        max_interv = model_metrics['supervisor_interventions'].max()
        if max_interv > 0:
            model_metrics['autonomy_norm'] = (1 - model_metrics['supervisor_interventions'] / max_interv) * 100
        else:
            model_metrics['autonomy_norm'] = 100
        
        # Create radar chart
        categories = ['Success\nRate', 'Speed', 'Cost\nEfficiency', 'Autonomy']
        num_vars = len(categories)
        
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        angles += angles[:1]
        
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6']
        
        for idx, row in model_metrics.iterrows():
            values = [
                row['success_norm'],
                row['speed_norm'],
                row['cost_eff_norm'],
                row['autonomy_norm']
            ]
            values += values[:1]
            
            ax.plot(angles, values, 'o-', linewidth=2, label=row['model'],
                   color=colors[idx % len(colors)])
            ax.fill(angles, values, alpha=0.15, color=colors[idx % len(colors)])
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=11, fontweight='bold')
        ax.set_ylim(0, 100)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=9)
        ax.grid(True, linestyle='--', alpha=0.7)
        
        plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=10)
        plt.title('Phase 2.1: Multi-Metric Model Comparison\n(Radar Chart)', 
                 fontsize=14, fontweight='bold', pad=20)
        
        self.save_plot('phase2_1_radar_chart.png')
        plt.show()
    
    # ========== PHASE 2.2 VISUALIZATIONS ==========
    
    def plot_phase2_2_ensemble_comparison(self):
        """Plot ensemble strategy comparison (Experiment 2.2)"""
        phase2_2 = self.df[self.df['experiment_id'].str.contains('phase2_exp2.2')]
        
        if len(phase2_2) == 0:
            print("⚠️ No Phase 2.2 data found")
            return
        
        # Extract strategy from prompt_strategy
        strategy_map = {
            'ensemble_baseline': 'Baseline\n(Single Model)',
            'ensemble_majority_voting': 'Majority\nVoting',
            'ensemble_tiered': 'Tiered\nStrategy',
            'ensemble_confidence': 'Confidence\nRouting'
        }
        
        phase2_2['strategy_name'] = phase2_2['prompt_strategy'].map(strategy_map)
        
        # Calculate metrics by strategy
        strategy_metrics = phase2_2.groupby('strategy_name').agg({
            'success': ['mean', 'std', 'count'],
            'execution_time_seconds': 'mean',
            'estimated_cost_usd': 'mean'
        }).reset_index()
        
        strategy_metrics.columns = ['strategy', 'success_mean', 'success_std', 'count',
                                    'time_mean', 'cost_mean']
        strategy_metrics['success_mean'] *= 100
        strategy_metrics['success_std'] *= 100
        strategy_metrics['ci'] = 1.96 * strategy_metrics['success_std'] / np.sqrt(strategy_metrics['count'])
        
        # Calculate efficiency (success per unit cost)
        strategy_metrics['efficiency'] = strategy_metrics['success_mean'] / (strategy_metrics['cost_mean'] * 10000)
        
        # Create 4-panel comparison
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Define order
        order = ['Baseline\n(Single Model)', 'Majority\nVoting', 'Tiered\nStrategy', 'Confidence\nRouting']
        strategy_metrics = strategy_metrics.set_index('strategy').reindex(order).reset_index()
        
        x = np.arange(len(strategy_metrics))
        colors = ['#95a5a6', '#3498db', '#e74c3c', '#2ecc71']
        
        # 1. Success Rate
        ax = axes[0, 0]
        bars = ax.bar(x, strategy_metrics['success_mean'], yerr=strategy_metrics['ci'],
                     capsize=5, alpha=0.8, edgecolor='black', linewidth=1.5)
        for bar, color in zip(bars, colors):
            bar.set_color(color)
        
        ax.set_ylabel('Success Rate (%)', fontsize=12, fontweight='bold')
        ax.set_title('Success Rate by Ensemble Strategy', fontsize=13, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(strategy_metrics['strategy'], fontsize=10)
        ax.set_ylim([0, 105])
        ax.axhline(y=strategy_metrics['success_mean'].iloc[0], color='gray', 
                  linestyle='--', alpha=0.5, label='Baseline')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        for i, v in enumerate(strategy_metrics['success_mean']):
            ax.text(i, v + strategy_metrics['ci'].iloc[i] + 2, f"{v:.1f}%",
                   ha='center', va='bottom', fontweight='bold', fontsize=10)
        
        # 2. Execution Time
        ax = axes[0, 1]
        bars = ax.bar(x, strategy_metrics['time_mean'], alpha=0.8, 
                     edgecolor='black', linewidth=1.5)
        for bar, color in zip(bars, colors):
            bar.set_color(color)
        
        ax.set_ylabel('Avg Execution Time (s)', fontsize=12, fontweight='bold')
        ax.set_title('Execution Time by Strategy', fontsize=13, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(strategy_metrics['strategy'], fontsize=10)
        ax.axhline(y=strategy_metrics['time_mean'].iloc[0], color='gray',
                  linestyle='--', alpha=0.5, label='Baseline')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        for i, v in enumerate(strategy_metrics['time_mean']):
            ax.text(i, v, f"{v:.1f}s", ha='center', va='bottom', 
                   fontweight='bold', fontsize=10)
        
        # 3. Cost
        ax = axes[1, 0]
        bars = ax.bar(x, strategy_metrics['cost_mean'], alpha=0.8,
                     edgecolor='black', linewidth=1.5)
        for bar, color in zip(bars, colors):
            bar.set_color(color)
        
        ax.set_ylabel('Avg Cost per Run ($)', fontsize=12, fontweight='bold')
        ax.set_title('Cost by Strategy', fontsize=13, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(strategy_metrics['strategy'], fontsize=10)
        ax.axhline(y=strategy_metrics['cost_mean'].iloc[0], color='gray',
                  linestyle='--', alpha=0.5, label='Baseline')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        for i, v in enumerate(strategy_metrics['cost_mean']):
            ax.text(i, v, f"${v:.4f}", ha='center', va='bottom',
                   fontweight='bold', fontsize=9)
        
        # 4. Efficiency (Success/Cost)
        ax = axes[1, 1]
        bars = ax.bar(x, strategy_metrics['efficiency'], alpha=0.8,
                     edgecolor='black', linewidth=1.5)
        for bar, color in zip(bars, colors):
            bar.set_color(color)
        
        ax.set_ylabel('Efficiency (Success per $0.0001)', fontsize=12, fontweight='bold')
        ax.set_title('Cost-Efficiency by Strategy', fontsize=13, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(strategy_metrics['strategy'], fontsize=10)
        ax.grid(axis='y', alpha=0.3)
        
        # Mark the best
        best_idx = strategy_metrics['efficiency'].idxmax()
        ax.scatter(best_idx, strategy_metrics['efficiency'].iloc[best_idx], 
                  s=200, marker='*', color='gold', edgecolor='black', 
                  linewidth=2, zorder=5, label='Best Efficiency')
        ax.legend()
        
        for i, v in enumerate(strategy_metrics['efficiency']):
            ax.text(i, v, f"{v:.1f}", ha='center', va='bottom',
                   fontweight='bold', fontsize=10)
        
        plt.suptitle('Phase 2.2: Ensemble Strategy Comparison', 
                     fontsize=16, fontweight='bold', y=0.995)
        plt.tight_layout()
        self.save_plot('phase2_2_ensemble_comparison.png')
        plt.show()
    
    def generate_all_visualizations(self):
        """Generate all visualizations"""
        print("\n" + "="*80)
        print("GENERATING ALL VISUALIZATIONS")
        print("="*80 + "\n")
        
        # Phase 1.1
        print("📊 Phase 1.1 Visualizations...")
        self.plot_phase1_1_success_rates()
        self.plot_phase1_1_execution_times()
        self.plot_phase1_1_cost_analysis()
        self.plot_phase1_1_failure_modes()
        
        # Phase 1.2
        print("\n📊 Phase 1.2 Visualizations...")
        self.plot_phase1_2_temperature_effect()
        self.plot_phase1_2_context_effect()
        self.plot_phase1_2_fewshot_effect()
        self.plot_phase1_2_constraint_effect()
        self.plot_phase1_2_heatmap()
        
        # Phase 2.1
        print("\n📊 Phase 2.1 Visualizations...")
        self.plot_phase2_1_model_comparison()
        self.plot_phase2_1_radar_chart()
        
        # Phase 2.2
        print("\n📊 Phase 2.2 Visualizations...")
        self.plot_phase2_2_ensemble_comparison()
        
        print("\n" + "="*80)
        print("✅ All visualizations complete!")
        print("📁 Saved in: experiment_results/")
        print("="*80)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Visualize LLM Mobile QA Experiments')
    parser.add_argument('--db', type=str, default='experiments.db',
                        help='Database file path')
    parser.add_argument('--phase', type=str, default='all',
                        choices=['1.1', '1.2', '2.1', '2.2', 'all'],
                        help='Which phase to visualize')
    
    args = parser.parse_args()
    
    viz = ExperimentVisualizer(db_path=args.db)
    
    if args.phase == 'all':
        viz.generate_all_visualizations()
    elif args.phase == '1.1':
        viz.plot_phase1_1_success_rates()
        viz.plot_phase1_1_execution_times()
        viz.plot_phase1_1_cost_analysis()
        viz.plot_phase1_1_failure_modes()
    elif args.phase == '1.2':
        viz.plot_phase1_2_temperature_effect()
        viz.plot_phase1_2_context_effect()
        viz.plot_phase1_2_fewshot_effect()
        viz.plot_phase1_2_constraint_effect()
        viz.plot_phase1_2_heatmap()
    elif args.phase == '2.1':
        viz.plot_phase2_1_model_comparison()
        viz.plot_phase2_1_radar_chart()
    elif args.phase == '2.2':
        viz.plot_phase2_2_ensemble_comparison()
