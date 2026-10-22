import sys
import os
import pandas as pd
import matplotlib.pyplot as plt

def process_marks_pipeline(csv_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    df = pd.read_csv(csv_path)

    subject_cols = [c for c in df.columns if c.lower() not in ('enrollment', 'name')]

    for col in subject_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        median_val = df[col].median()
        df[col] = df[col].fillna(median_val)

    df['Total'] = df[subject_cols].sum(axis=1)
    df['Average'] = df[subject_cols].mean(axis=1)

    cleaned_path = os.path.join(output_dir, 'cleaned_marks.csv')
    df.to_csv(cleaned_path, index=False)
    print(f"Exported: {cleaned_path}")

    summary_df = pd.DataFrame({
        'Mean': df[subject_cols].mean(),
        'Median': df[subject_cols].median(),
        'Std_Dev': df[subject_cols].std(),
        'Min': df[subject_cols].min(),
        'Max': df[subject_cols].max()
    })
    summary_path = os.path.join(output_dir, 'summary.csv')
    summary_df.to_csv(summary_path)
    print(f"Exported: {summary_path}")

    def assign_grade(score):
        if score >= 85: return 'A'
        if score >= 70: return 'B'
        if score >= 55: return 'C'
        if score >= 40: return 'D'
        return 'F'

    df['Grade'] = df['Average'].apply(assign_grade)
    grade_counts = df['Grade'].value_counts().sort_index()

    plt.figure(figsize=(6, 4))
    grade_counts.plot(kind='bar', color='steelblue', edgecolor='black')
    plt.title('Grade Distribution')
    plt.xlabel('Grade')
    plt.ylabel('Student Count')
    plt.tight_layout()
    chart1 = os.path.join(output_dir, 'grade_distribution.png')
    plt.savefig(chart1)
    plt.close()
    print(f"Saved: {chart1}")

    plt.figure(figsize=(6, 4))
    summary_df['Mean'].plot(kind='bar', color='teal', edgecolor='black')
    plt.title('Subject-wise Average Comparison')
    plt.xlabel('Subject')
    plt.ylabel('Average Marks')
    plt.tight_layout()
    chart2 = os.path.join(output_dir, 'subject_average.png')
    plt.savefig(chart2)
    plt.close()
    print(f"Saved: {chart2}")

    top_students = df.sort_values(by='Total', ascending=False).head(5)
    plt.figure(figsize=(6, 4))
    plt.barh(top_students['name'], top_students['Total'], color='coral', edgecolor='black')
    plt.title('Top Performers by Total Marks')
    plt.xlabel('Total Marks')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    chart3 = os.path.join(output_dir, 'top_performers.png')
    plt.savefig(chart3)
    plt.close()
    print(f"Saved: {chart3}")

if __name__ == '__main__':
    csv_input = sys.argv[1] if len(sys.argv) > 1 else 'marks.csv'
    out_dir = sys.argv[2] if len(sys.argv) > 2 else '.'
    process_marks_pipeline(csv_input, out_dir)
