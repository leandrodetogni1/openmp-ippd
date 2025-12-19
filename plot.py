import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from pathlib import Path

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 11
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['legend.fontsize'] = 10

RESULTS_DIR = Path("results")
PLOTS_DIR = Path("plots")

COLORS = {
    'seq': '#333333',
    'static': '#1f77b4',
    'dynamic': '#ff7f0e', 
    'guided': '#2ca02c',
    'critical': '#d62728',
    'atomic': '#9467bd',
    'local': '#17becf'
}

MARKERS = ['o', 's', '^', 'D', 'v', '<', '>']

def load_data():
    """Carrega os CSVs de resultados"""
    df_a = pd.read_csv(RESULTS_DIR / "task-a.csv")
    df_b = pd.read_csv(RESULTS_DIR / "task-b.csv")
    return df_a, df_b

def compute_stats(df, group_cols):
    """Calcula média e desvio padrão por grupo"""
    stats = df.groupby(group_cols)['time'].agg(['mean', 'std']).reset_index()
    stats.columns = group_cols + ['time_mean', 'time_std']
    return stats

def plot_task_a_schedule_comparison(df):
    """Gráfico comparando políticas de schedule para diferentes K"""
    PLOTS_DIR.mkdir(exist_ok=True)
    
    df_filtered = df[(df['variant'] == 'seq') | 
                     (df['schedule'] == 'static') |
                     ((df['schedule'].isin(['dynamic', 'guided'])) & (df['chunk'].isin([16, 1])))]
    
    for N in df['N'].unique():
        K_values = sorted(df['K'].unique())
        ncols = len(K_values)
        fig, axes = plt.subplots(1, ncols, figsize=(5*ncols, 5))
        if ncols == 1:
            axes = [axes]
        
        for idx, K in enumerate(K_values):
            ax = axes[idx]
            subset = df_filtered[(df_filtered['N'] == N) & (df_filtered['K'] == K)]
            
            seq_data = subset[subset['variant'] == 'seq']['time']
            seq_time = seq_data.mean() if len(seq_data) > 0 else 0
            
            for schedule in ['static', 'dynamic', 'guided']:
                data = subset[(subset['schedule'] == schedule)]
                if len(data) == 0:
                    continue
                    
                stats = compute_stats(data, ['threads'])
                ax.errorbar(stats['threads'], stats['time_mean'], 
                           yerr=stats['time_std'],
                           label=schedule, marker='o', capsize=3,
                           color=COLORS.get(schedule, '#666666'))
            
            ax.axhline(y=seq_time, color=COLORS['seq'], linestyle='--', 
                      label=f'seq ({seq_time:.2f}s)', alpha=0.7)
            
            ax.set_xlabel('Número de Threads')
            ax.set_ylabel('Tempo (s)')
            ax.set_title(f'K = {K}')
            ax.set_xticks([1, 2, 4, 8, 16])
            ax.legend()
            ax.set_ylim(bottom=0)
        
        fig.suptitle(f'Tarefa A: Comparação de Schedule (N = {N:,})', fontsize=14)
        plt.tight_layout()
        plt.savefig(PLOTS_DIR / f'task-a_schedule_N{N}.png', dpi=150, bbox_inches='tight')
        plt.close()
        print(f"  Salvo: task-a_schedule_N{N}.png")

def plot_task_a_chunk_impact(df):
    """Gráfico mostrando impacto do chunk size"""
    PLOTS_DIR.mkdir(exist_ok=True)
    
    N = df['N'].max() 
    K = 24
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    for idx, schedule in enumerate(['dynamic', 'guided']):
        ax = axes[idx]
        subset = df[(df['N'] == N) & (df['K'] == K) & (df['schedule'] == schedule)]
        
        for i, chunk in enumerate(sorted(subset['chunk'].unique())):
            if chunk == 0:
                continue
            data = subset[subset['chunk'] == chunk]
            stats = compute_stats(data, ['threads'])
            ax.errorbar(stats['threads'], stats['time_mean'],
                       yerr=stats['time_std'],
                       label=f'chunk={chunk}', marker=MARKERS[i], capsize=3)
        
        ax.set_xlabel('Número de Threads')
        ax.set_ylabel('Tempo (s)')
        ax.set_title(f'schedule({schedule}, chunk)')
        ax.set_xticks([1, 2, 4, 8, 16])
        ax.legend()
        ax.set_ylim(bottom=0)
    
    fig.suptitle(f'Tarefa A: Impacto do Chunk Size (N={N:,}, K={K})', fontsize=14)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'task-a_chunk_impact.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  Salvo: task-a_chunk_impact.png")

def plot_task_a_speedup(df):
    """Gráfico de speedup para Tarefa A"""
    PLOTS_DIR.mkdir(exist_ok=True)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    N_values = sorted(df['N'].unique())
    K_values = sorted(df['K'].unique())
    
    for i, N in enumerate(N_values):
        for j, K in enumerate(K_values):
            subset = df[(df['N'] == N) & (df['K'] == K)]
            if len(subset) == 0:
                continue
            
            seq_data = subset[subset['variant'] == 'seq']['time']
            if len(seq_data) == 0:
                continue
            seq_time = seq_data.mean()
            
            omp_data = subset[(subset['schedule'] == 'guided') & (subset['chunk'] == 16)]
            if len(omp_data) == 0:
                omp_data = subset[(subset['schedule'] == 'guided') & (subset['chunk'] == 1)]
            if len(omp_data) == 0:
                continue
                
            stats = compute_stats(omp_data, ['threads'])
            
            speedup = seq_time / stats['time_mean']
            ax.plot(stats['threads'], speedup, marker=MARKERS[i % len(MARKERS)], 
                   label=f'N={N:,}, K={K}')
    
    max_threads = int(df['threads'].max())
    threads = [t for t in [1, 2, 4, 8, 16] if t <= max_threads]
    ax.plot(threads, threads, 'k--', alpha=0.5, label='Speedup ideal')
    
    ax.set_xlabel('Número de Threads')
    ax.set_ylabel('Speedup')
    ax.set_title('Tarefa A: Speedup (schedule=guided)')
    ax.set_xticks(threads)
    ax.legend()
    ax.set_ylim(bottom=0)
    
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'task-a_speedup.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  Salvo: task-a_speedup.png")

def plot_task_b_variant_comparison(df):
    """Gráfico comparando critical vs atomic vs local"""
    PLOTS_DIR.mkdir(exist_ok=True)
    
    for N in df['N'].unique():
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        for idx, B in enumerate(sorted(df['B'].unique())):
            ax = axes[idx]
            subset = df[(df['N'] == N) & (df['B'] == B)]
            
            seq_time = subset[subset['variant'] == 'seq']['time'].mean()
            
            for variant in ['critical', 'atomic', 'local']:
                data = subset[subset['variant'] == variant]
                if len(data) == 0:
                    continue
                stats = compute_stats(data, ['threads'])
                ax.errorbar(stats['threads'], stats['time_mean'],
                           yerr=stats['time_std'],
                           label=variant, marker='o', capsize=3,
                           color=COLORS.get(variant, '#666666'))
            
            ax.axhline(y=seq_time, color=COLORS['seq'], linestyle='--',
                      label=f'seq ({seq_time*1000:.2f}ms)', alpha=0.7)
            
            ax.set_xlabel('Número de Threads')
            ax.set_ylabel('Tempo (s)')
            ax.set_title(f'B = {B}')
            ax.set_xticks([1, 2, 4, 8, 16])
            ax.legend()
            ax.set_ylim(bottom=0)
        
        fig.suptitle(f'Tarefa B: Comparação de Variantes (N = {N:,})', fontsize=14)
        plt.tight_layout()
        plt.savefig(PLOTS_DIR / f'task-b_variants_N{N}.png', dpi=150, bbox_inches='tight')
        plt.close()
        print(f"  Salvo: task-b_variants_N{N}.png")

def plot_task_b_scalability(df):
    """Gráfico de escalabilidade para Tarefa B"""
    PLOTS_DIR.mkdir(exist_ok=True)
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    variants = ['critical', 'atomic', 'local']
    
    N = df['N'].max()
    B = 256
    
    subset = df[(df['N'] == N) & (df['B'] == B)]
    seq_time = subset[subset['variant'] == 'seq']['time'].mean()
    
    for idx, variant in enumerate(variants):
        ax = axes[idx]
        data = subset[subset['variant'] == variant]
        stats = compute_stats(data, ['threads'])
        
        ax.bar(range(len(stats)), stats['time_mean'], 
               yerr=stats['time_std'], capsize=3,
               color=COLORS.get(variant, '#666666'), alpha=0.8)
        
        ax.axhline(y=seq_time, color=COLORS['seq'], linestyle='--', 
                  label=f'seq', alpha=0.7)
        
        ax.set_xlabel('Número de Threads')
        ax.set_ylabel('Tempo (s)')
        ax.set_title(f'Variante: {variant}')
        ax.set_xticks(range(len(stats)))
        ax.set_xticklabels(stats['threads'])
        ax.legend()
    
    fig.suptitle(f'Tarefa B: Escalabilidade por Variante (N={N:,}, B={B})', fontsize=14)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'task-b_scalability.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  Salvo: task-b_scalability.png")

def plot_task_b_speedup(df):
    """Gráfico de speedup para Tarefa B"""
    PLOTS_DIR.mkdir(exist_ok=True)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    N = df['N'].max()
    B = 256
    
    subset = df[(df['N'] == N) & (df['B'] == B)]
    seq_time = subset[subset['variant'] == 'seq']['time'].mean()
    
    for i, variant in enumerate(['critical', 'atomic', 'local']):
        data = subset[subset['variant'] == variant]
        stats = compute_stats(data, ['threads'])
        speedup = seq_time / stats['time_mean']
        ax.plot(stats['threads'], speedup, marker=MARKERS[i],
               label=variant, color=COLORS.get(variant, '#666666'))
    
    threads = [1, 2, 4, 8, 16]
    ax.plot(threads, threads, 'k--', alpha=0.5, label='Speedup ideal')
    
    ax.set_xlabel('Número de Threads')
    ax.set_ylabel('Speedup')
    ax.set_title(f'Tarefa B: Speedup (N={N:,}, B={B})')
    ax.set_xticks([1, 2, 4, 8, 16])
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'task-b_speedup.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  Salvo: task-b_speedup.png")

def generate_summary_table(df_a, df_b):
    """Gera tabelas resumo em Markdown"""
    PLOTS_DIR.mkdir(exist_ok=True)
    
    with open(PLOTS_DIR / 'summary_tables.md', 'w') as f:
        f.write("# Tabelas dos Resultados\n\n")
        
        f.write("## Tarefa A - Laço Irregular e Schedule\n\n")
        f.write("### Melhores tempos por configuração\n\n")
        
        stats_a = compute_stats(df_a[df_a['variant'] == 'omp'], 
                               ['N', 'K', 'schedule', 'chunk', 'threads'])
        
        f.write("| N | K | Melhor Schedule | Chunk | Threads | Tempo (s) | Speedup |\n")
        f.write("|---|---|-----------------|-------|---------|-----------|--------|\n")
        
        for N in sorted(df_a['N'].unique()):
            for K in sorted(df_a['K'].unique()):
                seq_time = df_a[(df_a['N'] == N) & (df_a['K'] == K) & 
                               (df_a['variant'] == 'seq')]['time'].mean()
                
                subset = stats_a[(stats_a['N'] == N) & (stats_a['K'] == K)]
                if len(subset) == 0:
                    continue
                    
                best = subset.loc[subset['time_mean'].idxmin()]
                speedup = seq_time / best['time_mean']
                f.write(f"| {N:,} | {K} | {best['schedule']} | {int(best['chunk'])} | "
                       f"{int(best['threads'])} | {best['time_mean']:.4f} | {speedup:.2f}x |\n")
        
        f.write("\n## Tarefa B - Histograma\n\n")
        f.write("### Comparação de variantes (melhor tempo por variante)\n\n")
        
        f.write("| N | B | Variante | Threads | Tempo (s) | Speedup |\n")
        f.write("|---|---|----------|---------|-----------|--------|\n")
        
        for N in sorted(df_b['N'].unique()):
            for B in sorted(df_b['B'].unique()):
                seq_time = df_b[(df_b['N'] == N) & (df_b['B'] == B) & 
                               (df_b['variant'] == 'seq')]['time'].mean()
                
                for variant in ['critical', 'atomic', 'local']:
                    subset = df_b[(df_b['N'] == N) & (df_b['B'] == B) & 
                                 (df_b['variant'] == variant)]
                    if len(subset) == 0:
                        continue
                    
                    stats = compute_stats(subset, ['threads'])
                    best = stats.loc[stats['time_mean'].idxmin()]
                    speedup = seq_time / best['time_mean']
                    f.write(f"| {N:,} | {B} | {variant} | {int(best['threads'])} | "
                           f"{best['time_mean']:.6f} | {speedup:.2f}x |\n")
    
    print("  Salvo: summary_tables.md")

def main():
    print("=" * 50)
    print("Gerando Gráficos")
    print("=" * 50)
    
    if not (RESULTS_DIR / "task-a.csv").exists():
        print(f"Erro: {RESULTS_DIR}/task-a.csv não encontrado.")
        print("Execute primeiro: ./run.sh")
        return
    
    if not (RESULTS_DIR / "task-b.csv").exists():
        print(f"Erro: {RESULTS_DIR}/task-b.csv não encontrado.")
        print("Execute primeiro: ./run.sh")
        return
    
    print("\nCarregando dados...")
    df_a, df_b = load_data()
    
    PLOTS_DIR.mkdir(exist_ok=True)
    
    print("\nGerando gráficos da Tarefa A...")
    try:
        plot_task_a_schedule_comparison(df_a)
        plot_task_a_chunk_impact(df_a)
        plot_task_a_speedup(df_a)
    except Exception as e:
        print(f"  Erro: {e}")
    
    print("\nGerando gráficos da Tarefa B...")
    try:
        plot_task_b_variant_comparison(df_b)
        plot_task_b_scalability(df_b)
        plot_task_b_speedup(df_b)
    except Exception as e:
        print(f"  Erro: {e}")
    
    print("\nGerando tabelas resumo...")
    try:
        generate_summary_table(df_a, df_b)
    except Exception as e:
        print(f"  Erro: {e}")
    
    print(f"  Gráficos salvos em: {PLOTS_DIR}/")

if __name__ == "__main__":
    main()
