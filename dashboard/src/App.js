// dashboard/src/App.js
import React, { useState, useEffect, useCallback, useMemo } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, TimeScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler } from 'chart.js';
import 'chartjs-adapter-moment';
import './App.css';

ChartJS.register(TimeScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler);

const API_BASE_URL = 'http://localhost:8000';

const chartColors = [
    { border: '#3B82F6', bg: 'rgba(59, 130, 246, 0.1)' }, { border: '#EF4444', bg: 'rgba(239, 68, 68, 0.1)' },
    { border: '#10B981', bg: 'rgba(16, 185, 129, 0.1)' }, { border: '#F59E0B', bg: 'rgba(245, 158, 11, 0.1)' },
    { border: '#8B5CF6', bg: 'rgba(139, 92, 246, 0.1)' }, { border: '#EC4899', bg: 'rgba(236, 72, 153, 0.1)' },
    { border: '#14B8A6', bg: 'rgba(20, 184, 166, 0.1)' }, { border: '#A855F7', bg: 'rgba(168, 85, 247, 0.1)' },
    { border: '#EAB308', bg: 'rgba(234, 179, 8, 0.1)' }, { border: '#6D28D9', bg: 'rgba(109, 40, 217, 0.1)' },
    { border: '#F97316', bg: 'rgba(249, 115, 22, 0.1)' }, { border: '#6366F1', bg: 'rgba(99, 102, 241, 0.1)' },
    { border: '#EC4899', bg: 'rgba(236, 72, 153, 0.1)' },
];
const chartOptions = {
    responsive: true, maintainAspectRatio: false,
    plugins: { legend: { labels: { color: '#1e2a3b' } } },
    scales: {
        y: { ticks: { color: '#5a687d' }, grid: { color: '#e6e9f0' } },
        x: { 
            type: 'time',
            ticks: { color: '#5a687d', autoSkip: true, maxTicksLimit: 20 },
            grid: { display: false },
            time: { unit: 'minute', displayFormats: { minute: 'HH:mm' } }
        }
    },
    animation: { duration: 400 },
    elements: { line: { spanGaps: true } }
};

const App = () => {
    const [devices, setDevices] = useState({});
    const [selectedDevice, setSelectedDevice] = useState('');
    const [dashboardData, setDashboardData] = useState({
        latest_metrics: {}, trends: { datasets: [] },
        daily_averages_table: [], overall_weekly_averages: {}
    });
    const [alerts, setAlerts] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [refreshKey, setRefreshKey] = useState(0);

    const fetchData = useCallback(async () => {
        if (!selectedDevice) return;
        setIsLoading(true);
        try {
            const [deviceRes, alertsRes] = await Promise.all([
                axios.get(`${API_BASE_URL}/devices/${selectedDevice}/analytics`),
                axios.get(`${API_BASE_URL}/alerts`)
            ]);

            console.log('Trends Data:', JSON.stringify(deviceRes.data.trends, null, 2));

            const newTrendsData = {
                datasets: deviceRes.data.trends.datasets.map((ds, i) => ({
                    ...ds,
                    borderColor: chartColors[i % chartColors.length].border,
                    backgroundColor: chartColors[i % chartColors.length].bg,
                    fill: true,
                    tension: 0.4,
                    borderWidth: 2,
                    pointBackgroundColor: chartColors[i % chartColors.length].border,
                    pointRadius: 3,
                    pointHoverRadius: 6,
                    spanGaps: true,
                    data: ds.data.map(d => ({ ...d }))  // Deep clone objects
                }))
            };

            setDashboardData({ ...deviceRes.data, trends: newTrendsData });
            setAlerts(alertsRes.data);
            setRefreshKey(oldKey => oldKey + 1);
        } catch (error) {
            console.error(`Error fetching data for ${selectedDevice}:`, error);
        } finally {
            setIsLoading(false);
        }
    }, [selectedDevice]);

    useEffect(() => {
        const fetchDeviceList = async () => {
            try {
                const res = await axios.get(`${API_BASE_URL}/devices`);
                setDevices(res.data);
                if (res.data && Object.keys(res.data).length > 0) {
                    setSelectedDevice(Object.values(res.data)[0][0]);
                }
            } catch (error) { console.error("Error fetching device list:", error); }
        };
        fetchDeviceList();
    }, []);

    useEffect(() => { fetchData(); }, [fetchData, selectedDevice]);

    const pivotedDailyAverages = useMemo(() => {
        const dates = [...new Set(dashboardData.daily_averages_table.map(([date]) => new Date(date).toLocaleDateString()))].sort((a, b) => new Date(b) - new Date(a));
        const params = [...new Set(dashboardData.daily_averages_table.map(([, name]) => name.replace(/_/g, ' ')))].sort();
        const dataMap = dashboardData.daily_averages_table.reduce((acc, [date, name, avg]) => {
            const dateKey = new Date(date).toLocaleDateString();
            const paramKey = name.replace(/_/g, ' ');
            if (!acc[dateKey]) acc[dateKey] = {};
            acc[dateKey][paramKey] = Number(avg).toFixed(2);
            return acc;
        }, {});

        return { dates, params, dataMap };
    }, [dashboardData.daily_averages_table]);

    return (
        <div className="dashboard-layout">
            <aside className="sidebar">
                <div className="sidebar-header"><h2>DEVICES</h2></div>
                {Object.entries(devices).map(([type, list]) => (
                    <div key={type} className="device-group">
                        <h3>{type}</h3>
                        <select onChange={e => setSelectedDevice(e.target.value)} value={selectedDevice}>
                            {list.map(d => <option key={d} value={d}>{d}</option>)}
                        </select>
                    </div>
                ))}
            </aside>
            <header className="main-header">
                <h1>Dashboard for {selectedDevice}</h1>
                <button onClick={fetchData} disabled={isLoading}>{isLoading ? 'Refreshing...' : 'Refresh Data'}</button>
            </header>
            <main className="main-content">
                <section className="data-section">
                    <h3>Live Metrics</h3>
                    <div className="metrics-grid">
                        {isLoading ? <p className="loading-text">Loading...</p> : Object.entries(dashboardData.latest_metrics).map(([name, value]) => (
                            <div key={name} className="metric-card"><h4>{name.replace(/_/g, ' ')}</h4><p>{value}</p></div>
                        ))}
                    </div>
                </section>
                <section className="data-section">
                    <h3>24-Hour Trends</h3>
                    <div className="chart-container">
                        {isLoading ? <p className="loading-text">Loading chart...</p> : (
                            <Line key={refreshKey} options={chartOptions} data={dashboardData.trends} />
                        )}
                    </div>
                </section>
                <section className="data-section">
                    <h3>7-Day Daily Averages</h3>
                    <div className="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>Date</th>
                                    {pivotedDailyAverages.params.map(param => <th key={param}>{param}</th>)}
                                </tr>
                            </thead>
                            <tbody>
                                {pivotedDailyAverages.dates.map(date => (
                                    <tr key={date}>
                                        <td>{date}</td>
                                        {pivotedDailyAverages.params.map(param => (
                                            <td key={param}>{pivotedDailyAverages.dataMap[date]?.[param] || '-'}</td>
                                        ))}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </section>
                <section className="data-section">
                    <h3>Overall 7-Day Averages</h3>
                    <div className="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>Parameter</th>
                                    <th>Average Value</th>
                                </tr>
                            </thead>
                            <tbody>
                                {isLoading ? <tr><td colSpan="2" className="loading-text">Loading...</td></tr> : Object.entries(dashboardData.overall_weekly_averages).map(([name, value]) => (
                                    <tr key={name}>
                                        <td>{name.replace(/_/g, ' ')}</td>
                                        <td>{value}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </section>
                <section className="data-section">
                    <h3>Recent Alerts</h3>
                    <div className="table-container">
                        <table>
                            <thead><tr><th>Time</th><th>Device</th><th>Message</th><th>Severity</th></tr></thead>
                            <tbody>
                                {alerts.map((alert, i) => (
                                    <tr key={i}><td>{new Date(alert.time).toLocaleString()}</td><td>{alert.device_name}</td><td>{alert.message}</td><td className={`severity-${alert.severity.toLowerCase()}`}>{alert.severity}</td></tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </section>
            </main>
        </div>
    );
};

export default App;