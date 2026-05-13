<template>
  <div class="reports-page">
    <div class="page-header">
      <div>
        <h1 class="page-title"><i class="pi pi-chart-bar"></i> Отчёты и статистика</h1>
        <p class="page-subtitle">Аналитика по выдачам, читателям и фонду</p>
      </div>
    </div>

    <!-- Filters Card -->
    <div class="glass settings-card mb-8">
      <h3 class="card-header"><i class="pi pi-filter"></i> Параметры отчёта</h3>
      <div class="card-body">
        <div class="filters-row">
          <div class="filter-item">
            <label class="filter-label">Тип отчёта</label>
            <Dropdown v-model="filters.reportType" :options="reportTypes" optionLabel="label" optionValue="value" class="w-full" />
          </div>
          <div class="filter-item">
            <label class="filter-label">Период</label>
            <Dropdown v-model="filters.period" :options="periods" optionLabel="label" optionValue="value" class="w-full" />
          </div>
          <div v-if="filters.period === 'custom'" class="filter-item">
            <label class="filter-label">С</label>
            <Calendar v-model="filters.dateFrom" dateFormat="dd.mm.yy" class="w-full" :manualInput="false" />
          </div>
          <div v-if="filters.period === 'custom'" class="filter-item">
            <label class="filter-label">По</label>
            <Calendar v-model="filters.dateTo" dateFormat="dd.mm.yy" class="w-full" :manualInput="false" />
          </div>
        </div>
        
        <div class="flex gap-3 mt-4">
          <Button label="Сбросить" icon="pi pi-refresh" class="p-button-outlined p-button-sm" @click="resetReports" :disabled="loading" />
          <Button label="Сформировать" icon="pi pi-chart-bar" :loading="loading" @click="generateReport" />
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading && !stats" class="glass p-12 text-center">
      <ProgressSpinner class="w-12 h-12 mb-4" />
      <p class="text-secondary">Генерация отчёта...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="glass p-8 text-center border-red-500/20 border">
      <i class="pi pi-exclamation-triangle text-3xl text-red-500 mb-3"></i>
      <p class="text-secondary mb-4">{{ error }}</p>
      <Button label="Повторить" icon="pi pi-refresh" @click="generateReport" />
    </div>

    <!-- Charts Area -->
    <template v-else-if="stats">
      <div class="charts-wrapper">
        
        <!-- Столбчатый график -->
        <div v-if="filters.reportType === 'loans' || filters.reportType === 'all'" class="glass chart-card">
          <h3 class="chart-title"><i class="pi pi-chart-bar" style="color: var(--primary);"></i> Динамика выдач книг</h3>
          <div class="chart-container-large">
            <Bar v-if="loansChart" :data="loansChart" :options="chartOptions" />
          </div>
        </div>

        <!-- Линейный график -->
        <div v-if="filters.reportType === 'activity' || filters.reportType === 'all'" class="glass chart-card">
          <h3 class="chart-title"><i class="pi pi-chart-line" style="color: var(--secondary);"></i> Активность: выдачи и возвраты</h3>
          <div class="chart-container-large">
            <Line v-if="activityChart" :data="activityChart" :options="lineOptions" />
          </div>
        </div>

        <!-- Круговая диаграмма -->
        <div v-if="filters.reportType === 'genres' || filters.reportType === 'all'" class="glass chart-card">
          <h3 class="chart-title"><i class="pi pi-tags" style="color: var(--warning);"></i> Распределение по жанрам</h3>
          <div class="chart-container">
            <Doughnut v-if="genresChart" :data="genresChart" :options="doughnutOptions" />
          </div>
        </div>

        <!-- Статистика -->
        <div class="stats-grid">
          <div class="glass stat-card accent-blue">
            <div class="stat-info"><h3>Всего выдач</h3><p>{{ stats?.totalLoans ?? '—' }}</p></div>
            <i class="pi pi-upload stat-icon" style="color: #3b82f6;"></i>
          </div>
          <div class="glass stat-card accent-green">
            <div class="stat-info"><h3>Возвращено</h3><p>{{ stats?.returned ?? '—' }}</p></div>
            <i class="pi pi-check-circle stat-icon" style="color: #10b981;"></i>
          </div>
          <div class="glass stat-card accent-cyan">
            <div class="stat-info"><h3>На руках</h3><p>{{ stats?.active ?? '—' }}</p></div>
            <i class="pi pi-book stat-icon" style="color: #06b6d4;"></i>
          </div>
          <div class="glass stat-card accent-red">
            <div class="stat-info"><h3>Просрочено</h3><p>{{ stats?.overdue ?? '—' }}</p></div>
            <i class="pi pi-exclamation-triangle stat-icon" style="color: #ef4444;"></i>
          </div>
        </div>

        <!-- Топ книг -->
        <div v-if="filters.reportType === 'top' || filters.reportType === 'all'" class="glass chart-card full-width">
          <h3 class="chart-title"><i class="pi pi-star" style="color: var(--warning);"></i> Топ-5 популярных книг</h3>
          <DataTable :value="topBooks" stripedRows class="border-none" emptyMessage="Данные не найдены">
            <Column field="rank" header="#" style="width: 60px"></Column>
            <Column field="title" header="Название"></Column>
            <Column field="author" header="Автор"></Column>
            <Column field="loansCount" header="Выдач" style="width: 100px">
              <template #body="{ data }"><Tag :value="data.loansCount" severity="info" /></template>
            </Column>
          </DataTable>
        </div>

      </div>
    </template>

    <!-- Empty State -->
    <div v-else class="glass empty-state">
      <i class="pi pi-chart-bar text-6xl mb-4" style="color: var(--text-secondary); opacity: 0.3;"></i>
      <p class="text-secondary">Выберите параметры и нажмите "Сформировать" для генерации отчёта</p>
    </div>

  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useReports } from '../../composables/useReports'
import { useToast } from 'primevue/usetoast'
import { Bar, Doughnut, Line } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, ArcElement, LineElement, PointElement, Title, Tooltip, Legend } from 'chart.js'
import Dropdown from 'primevue/dropdown'
import Calendar from 'primevue/calendar'
import Button from 'primevue/button'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'
import ProgressSpinner from 'primevue/progressspinner'

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, LineElement, PointElement, Title, Tooltip, Legend)

// ✅ Деструктуризация решает проблему с передачей Ref-объекта в пропс
const { 
  loading, 
  error, 
  stats, 
  filters, 
  loansChart, 
  activityChart, 
  genresChart, 
  topBooks, 
  loadReports, 
  resetFilters 
} = useReports()

const toast = useToast()

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { labels: { color: '#b3b3b3', font: { size: 11 } } } },
  scales: {
    x: { ticks: { color: '#b3b3b3' }, grid: { color: 'rgba(255,255,255,0.05)' } },
    y: { ticks: { color: '#b3b3b3' }, grid: { color: 'rgba(255,255,255,0.05)' }, beginAtZero: true }
  }
}

const lineOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: { mode: 'index', intersect: false },
  plugins: {
    legend: { labels: { color: '#b3b3b3', font: { size: 11 } } },
    tooltip: { backgroundColor: 'rgba(30, 30, 30, 0.95)', titleColor: '#fff', bodyColor: '#b3b3b3', borderColor: 'rgba(255,255,255,0.1)', borderWidth: 1, padding: 12 }
  },
  scales: {
    x: { ticks: { color: '#b3b3b3' }, grid: { color: 'rgba(255,255,255,0.05)' } },
    y: { ticks: { color: '#b3b3b3' }, grid: { color: 'rgba(255,255,255,0.05)' }, beginAtZero: true }
  }
}

const doughnutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: '65%',
  plugins: {
    legend: { position: 'right', labels: { color: '#b3b3b3', font: { size: 11 }, padding: 12, usePointStyle: true } },
    tooltip: { backgroundColor: 'rgba(30, 30, 30, 0.95)', titleColor: '#fff', bodyColor: '#b3b3b3', borderColor: 'rgba(255,255,255,0.1)', borderWidth: 1, padding: 12 }
  },
  animation: { animateScale: true, animateRotate: true }
}

const reportTypes = [
  { label: 'Все отчёты', value: 'all' },
  { label: 'Выдачи', value: 'loans' },
  { label: 'Активность', value: 'activity' },
  { label: 'Жанры', value: 'genres' },
  { label: 'Топ книг', value: 'top' }
]

const periods = [
  { label: 'Месяц', value: 'month' },
  { label: 'Квартал', value: 'quarter' },
  { label: 'Год', value: 'year' },
  { label: 'Произвольно', value: 'custom' }
]

onMounted(() => {})

const generateReport = async () => {
  const result = await loadReports()
  if (result.success) toast.add({ severity: 'success', summary: 'Готово', detail: 'Отчёт сформирован', life: 2000 })
  else toast.add({ severity: 'error', summary: 'Ошибка', detail: error, life: 4000 })
}

const resetReports = () => {
  resetFilters()
  toast.add({ severity: 'info', summary: 'Сброшено', detail: 'Фильтры очищены', life: 2000 })
}
</script>

<style scoped>
.filters-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 0; }
.filter-item { display: flex; flex-direction: column; gap: 6px; }
.filter-label { font-size: 12px; font-weight: 500; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.3px; }
.filters-row .p-dropdown { background: rgba(255, 255, 255, 0.04) !important; border: 1px solid var(--glass-border) !important; border-radius: 10px !important; height: 42px !important; }
.filters-row .p-dropdown .p-dropdown-label { padding: 0 38px 0 16px !important; color: var(--text-primary) !important; line-height: 42px !important; text-align: center !important; display: flex !important; align-items: center !important; justify-content: center !important; }
.filters-row .p-dropdown .p-dropdown-trigger { color: var(--text-secondary) !important; width: 42px !important; display: flex !important; align-items: center !important; justify-content: center !important; }
.filters-row .p-dropdown:not(.p-disabled).p-focus { border-color: var(--primary) !important; box-shadow: 0 0 0 3px rgba(187, 134, 252, 0.15) !important; background: rgba(255, 255, 255, 0.07) !important; }

.charts-wrapper { display: flex; flex-direction: column; gap: 24px; }
.chart-card { padding: 28px; border-radius: var(--radius-lg); }
.chart-title { font-size: 17px; font-weight: 600; color: var(--text-primary); margin: 0 0 24px 0; display: flex; align-items: center; gap: 10px; }
.chart-container-large { position: relative; height: 350px; width: 100%; }
.chart-container { position: relative; height: 280px; width: 100%; display: flex; align-items: center; justify-content: center; }
.empty-state { padding: 80px 24px; text-align: center; border-radius: var(--radius-lg); }
.full-width { grid-column: 1 / -1; }

.chart-card { animation: fadeIn 0.4s ease-out; }
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 900px) {
  .chart-container-large { height: 280px; }
  .chart-container { height: 240px; }
}
</style>