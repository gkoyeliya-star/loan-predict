"""
Create a visual flowchart showing how the model works
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Loan Approval Prediction System - Visual Explanation', fontsize=18, fontweight='bold')

# ===== DIAGRAM 1: Training Process =====
ax1 = axes[0, 0]
ax1.set_xlim(0, 10)
ax1.set_ylim(0, 10)
ax1.axis('off')
ax1.set_title('1. Model Training Process', fontsize=14, fontweight='bold', pad=20)

# Training flow
boxes_train = [
    (5, 9, "Generate 1000\nLoan Applications"),
    (5, 7.5, "Encode Categories\n(Male→0, Yes→1, etc.)"),
    (5, 6, "Split: 800 Train\n200 Test"),
    (5, 4.5, "Train 3 Models:\nDecision Tree, SVM,\nRandom Forest"),
    (5, 3, "Evaluate Accuracy\nCross-Validation"),
    (5, 1.5, "Best Model: Random Forest\n96.5% Accuracy ⭐"),
]

for x, y, text in boxes_train:
    box = FancyBboxPatch((x-1.5, y-0.4), 3, 0.8, boxstyle="round,pad=0.1",
                         edgecolor='#667eea', facecolor='#e8eaf6', linewidth=2)
    ax1.add_patch(box)
    ax1.text(x, y, text, ha='center', va='center', fontsize=9, fontweight='bold')
    
    if y > 1.5:
        arrow = FancyArrowPatch((x, y-0.5), (x, y-1), 
                               arrowstyle='->', mutation_scale=20, 
                               linewidth=2, color='#667eea')
        ax1.add_patch(arrow)

# ===== DIAGRAM 2: Feature Importance =====
ax2 = axes[0, 1]
ax2.set_title('2. What the Model Learned (Feature Importance)', fontsize=14, fontweight='bold', pad=20)

features = ['Credit History', 'Applicant Income', 'Coapp. Income', 'Loan Amount', 
            'Loan Term', 'Dependents', 'Property Area', 'Education', 'Married', 'Gender', 'Self Employed']
importance = [0.419, 0.151, 0.124, 0.111, 0.044, 0.040, 0.040, 0.023, 0.019, 0.016, 0.013]

colors = ['#d32f2f' if i == 0 else '#ff9800' if i < 4 else '#4caf50' for i in range(len(features))]
bars = ax2.barh(features, importance, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)

ax2.set_xlabel('Importance Score', fontsize=11, fontweight='bold')
ax2.set_xlim(0, 0.45)
ax2.grid(axis='x', alpha=0.3, linestyle='--')

# Add percentage labels
for i, (feat, imp) in enumerate(zip(features, importance)):
    ax2.text(imp + 0.01, i, f'{imp*100:.1f}%', va='center', fontsize=9, fontweight='bold')

# Add legend
legend_elements = [
    mpatches.Patch(color='#d32f2f', label='Critical (>40%)'),
    mpatches.Patch(color='#ff9800', label='Important (10-20%)'),
    mpatches.Patch(color='#4caf50', label='Minor (<5%)')
]
ax2.legend(handles=legend_elements, loc='lower right', fontsize=9)

# ===== DIAGRAM 3: Prediction Flow =====
ax3 = axes[1, 0]
ax3.set_xlim(0, 10)
ax3.set_ylim(0, 10)
ax3.axis('off')
ax3.set_title('3. How Predictions Work (Random Forest)', fontsize=14, fontweight='bold', pad=20)

# User input box
input_box = FancyBboxPatch((0.5, 8), 3, 1.5, boxstyle="round,pad=0.1",
                          edgecolor='#4caf50', facecolor='#e8f5e9', linewidth=2)
ax3.add_patch(input_box)
ax3.text(2, 9.3, 'User Application', ha='center', fontsize=10, fontweight='bold')
ax3.text(2, 8.7, 'Income: $7000', ha='center', fontsize=8)
ax3.text(2, 8.4, 'Credit: Good', ha='center', fontsize=8)

# Arrow to trees
arrow1 = FancyArrowPatch((3.5, 8.75), (5, 7.5), 
                        arrowstyle='->', mutation_scale=20, 
                        linewidth=2, color='#667eea')
ax3.add_patch(arrow1)

# 100 trees
tree_box = FancyBboxPatch((4, 6), 4, 3, boxstyle="round,pad=0.1",
                         edgecolor='#667eea', facecolor='#e3f2fd', linewidth=2)
ax3.add_patch(tree_box)
ax3.text(6, 8.5, '100 Decision Trees', ha='center', fontsize=11, fontweight='bold')

# Individual tree examples
tree_texts = [
    'Tree 1: ✅ Approved',
    'Tree 2: ✅ Approved', 
    'Tree 3: ❌ Rejected',
    '...',
    'Tree 100: ✅ Approved'
]
for i, text in enumerate(tree_texts):
    ax3.text(6, 7.8 - i*0.35, text, ha='center', fontsize=8)

# Arrow to result
arrow2 = FancyArrowPatch((6, 5.8), (6, 4.5), 
                        arrowstyle='->', mutation_scale=20, 
                        linewidth=2, color='#667eea')
ax3.add_patch(arrow2)

# Voting box
vote_box = FancyBboxPatch((4.5, 3), 3, 1.3, boxstyle="round,pad=0.1",
                         edgecolor='#ff9800', facecolor='#fff3e0', linewidth=2)
ax3.add_patch(vote_box)
ax3.text(6, 4.1, 'Vote Tally', ha='center', fontsize=10, fontweight='bold')
ax3.text(6, 3.7, '✅ Approved: 87 trees', ha='center', fontsize=9, color='green')
ax3.text(6, 3.4, '❌ Rejected: 13 trees', ha='center', fontsize=9, color='red')

# Arrow to final result
arrow3 = FancyArrowPatch((6, 2.8), (6, 1.8), 
                        arrowstyle='->', mutation_scale=20, 
                        linewidth=2, color='#667eea')
ax3.add_patch(arrow3)

# Final result
result_box = FancyBboxPatch((4.5, 0.5), 3, 1.1, boxstyle="round,pad=0.1",
                           edgecolor='#4caf50', facecolor='#c8e6c9', linewidth=3)
ax3.add_patch(result_box)
ax3.text(6, 1.3, '✅ APPROVED', ha='center', fontsize=12, fontweight='bold', color='#1b5e20')
ax3.text(6, 0.8, 'Confidence: 87%', ha='center', fontsize=10, color='#1b5e20')

# ===== DIAGRAM 4: Credit History Impact =====
ax4 = axes[1, 1]
ax4.set_title('4. Credit History Impact (Most Important Factor)', fontsize=14, fontweight='bold', pad=20)

# Credit history comparison
categories = ['Bad Credit\n(0)', 'Good Credit\n(1)']
approval_rates = [45.6, 99.1]
colors_credit = ['#ef5350', '#66bb6a']

bars = ax4.bar(categories, approval_rates, color=colors_credit, alpha=0.8, 
               edgecolor='black', linewidth=2, width=0.6)

# Add percentage labels on bars
for i, (cat, rate) in enumerate(zip(categories, approval_rates)):
    ax4.text(i, rate + 2, f'{rate:.1f}%', ha='center', fontsize=14, fontweight='bold')
    
    # Add icons
    if i == 0:
        ax4.text(i, rate/2, '❌\nVery Hard', ha='center', fontsize=16, color='white', fontweight='bold')
    else:
        ax4.text(i, rate/2, '✅\nAlmost\nGuaranteed!', ha='center', fontsize=14, color='white', fontweight='bold')

ax4.set_ylabel('Approval Rate (%)', fontsize=11, fontweight='bold')
ax4.set_ylim(0, 110)
ax4.grid(axis='y', alpha=0.3, linestyle='--')
ax4.axhline(y=50, color='gray', linestyle='--', linewidth=1, alpha=0.5)
ax4.text(1.5, 52, '50% threshold', fontsize=8, style='italic')

# Add note
ax4.text(0.5, -15, 'Credit History accounts for 42% of the decision weight!', 
         ha='center', fontsize=10, style='italic', bbox=dict(boxstyle='round', 
         facecolor='yellow', alpha=0.3))

plt.tight_layout()
plt.savefig('model_logic_visual.png', dpi=300, bbox_inches='tight')
print("✓ Visual explanation saved as 'model_logic_visual.png'")
plt.close()

# Create a second figure for data patterns
fig2, axes2 = plt.subplots(2, 2, figsize=(14, 10))
fig2.suptitle('Training Data Patterns', fontsize=16, fontweight='bold')

# Income vs Approval
ax1 = axes2[0, 0]
income_cats = ['Low\n(<$3K)', 'Medium\n($3-5K)', 'High\n($5-8K)', 'Very High\n(>$8K)']
income_approval = [73.3, 88.6, 92.0, 94.1]
bars1 = ax1.bar(income_cats, income_approval, color=['#ef5350', '#ff9800', '#66bb6a', '#43a047'], 
                alpha=0.8, edgecolor='black', linewidth=1.5)
ax1.set_title('Income Level vs Approval Rate', fontsize=12, fontweight='bold')
ax1.set_ylabel('Approval Rate (%)', fontweight='bold')
ax1.set_ylim(0, 100)
for i, v in enumerate(income_approval):
    ax1.text(i, v + 2, f'{v:.1f}%', ha='center', fontweight='bold')
ax1.grid(axis='y', alpha=0.3)

# Education vs Approval
ax2 = axes2[0, 1]
edu_cats = ['Not Graduate', 'Graduate']
edu_approval = [85.9, 93.3]
bars2 = ax2.bar(edu_cats, edu_approval, color=['#ff9800', '#66bb6a'], 
                alpha=0.8, edgecolor='black', linewidth=1.5)
ax2.set_title('Education vs Approval Rate', fontsize=12, fontweight='bold')
ax2.set_ylabel('Approval Rate (%)', fontweight='bold')
ax2.set_ylim(0, 100)
for i, v in enumerate(edu_approval):
    ax2.text(i, v + 2, f'{v:.1f}%', ha='center', fontweight='bold')
ax2.grid(axis='y', alpha=0.3)

# Marriage vs Approval
ax3 = axes2[1, 0]
marry_cats = ['Single', 'Married']
marry_approval = [88.8, 93.4]
bars3 = ax3.bar(marry_cats, marry_approval, color=['#ff9800', '#66bb6a'], 
                alpha=0.8, edgecolor='black', linewidth=1.5)
ax3.set_title('Marital Status vs Approval Rate', fontsize=12, fontweight='bold')
ax3.set_ylabel('Approval Rate (%)', fontweight='bold')
ax3.set_ylim(0, 100)
for i, v in enumerate(marry_approval):
    ax3.text(i, v + 2, f'{v:.1f}%', ha='center', fontweight='bold')
ax3.grid(axis='y', alpha=0.3)

# Overall approval distribution
ax4 = axes2[1, 1]
overall_cats = ['Rejected', 'Approved']
overall_counts = [82, 918]
colors4 = ['#ef5350', '#66bb6a']
bars4 = ax4.bar(overall_cats, overall_counts, color=colors4, 
                alpha=0.8, edgecolor='black', linewidth=1.5)
ax4.set_title('Overall Training Data Distribution', fontsize=12, fontweight='bold')
ax4.set_ylabel('Number of Applications', fontweight='bold')
for i, v in enumerate(overall_counts):
    ax4.text(i, v + 20, f'{v}\n({v/10:.1f}%)', ha='center', fontweight='bold')
ax4.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('data_patterns.png', dpi=300, bbox_inches='tight')
print("✓ Data patterns visualization saved as 'data_patterns.png'")
plt.close()

print("\n✅ All visualizations created successfully!")
print("   - model_logic_visual.png (How the model works)")
print("   - data_patterns.png (Training data patterns)")
