// dashboard/src/App.js
import React, { useState, useEffect, useCallback, useMemo } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import {
    Chart as ChartJS, TimeScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler
} from 'chart.js';
import 'chartjs-adapter-moment';
import annotationPlugin from 'chartjs-plugin-annotation';
import { formatISO, subHours, isValid } from 'date-fns';

import './App.css';

// Register necessary Chart.js components AND the annotation plugin
ChartJS.register(TimeScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler, annotationPlugin);

const API_BASE_URL = 'http://localhost:8000';

// Chart Colors definition
const chartColors = [
    { border: '#3B82F6', bg: 'rgba(59, 130, 246, 0.1)' }, { border: '#EF4444', bg: 'rgba(239, 68, 68, 0.1)' },
    { border: '#10B981', bg: 'rgba(16, 185, 129, 0.1)' }, { border: '#F59E0B', bg: 'rgba(245, 158, 11, 0.1)' },
    { border: '#8B5CF6', bg: 'rgba(139, 92, 246, 0.1)' }, { border: '#EC4899', bg: 'rgba(236, 72, 153, 0.1)' },
    { border: '#14B8A6', bg: 'rgba(20, 184, 166, 0.1)' }, { border: '#A855F7', bg: 'rgba(168, 85, 247, 0.1)' },
    { border: '#EAB308', bg: 'rgba(234, 179, 8, 0.1)' }, { border: '#6D28D9', bg: 'rgba(109, 40, 217, 0.1)' },
    { border: '#F97316', bg: 'rgba(249, 115, 22, 0.1)' }, { border: '#6366F1', bg: 'rgba(99, 102, 241, 0.1)' },
];

const App = () => {
    // State Variables
    const [devices, setDevices] = useState({});
    const [selectedDevice, setSelectedDevice] = useState('');
    const [dashboardData, setDashboardData] = useState({
        latest_metrics: {},
        trends: { datasets: [] },
        daily_averages_table: [],
        overall_period_averages: {}
    });
    const [alerts, setAlerts] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [refreshKey, setRefreshKey] = useState(0);

    // --- State & Handlers for Time Range ---
    const getDefaultEndTime = () => new Date();
    const getDefaultStartTime = () => subHours(getDefaultEndTime(), 24);

    const [startTime, setStartTime] = useState(getDefaultStartTime);
    const [endTime, setEndTime] = useState(getDefaultEndTime);

    const handleStartTimeChange = (event) => {
        const newDate = new Date(event.target.value);
        if (isValid(newDate)) {
            setStartTime(newDate > endTime ? endTime : newDate);
        } else {
            setStartTime(getDefaultStartTime());
            setEndTime(getDefaultEndTime());
        }
    };

    const handleEndTimeChange = (event) => {
        const newDate = new Date(event.target.value);
        if (isValid(newDate)) {
            setEndTime(newDate < startTime ? startTime : newDate);
        } else {
            setStartTime(getDefaultStartTime());
            setEndTime(getDefaultEndTime());
        }
    };
    // --- End Time Range ---

    // --- Chart Options with Annotations (Memoized) ---
    const chartOptions = useMemo(() => {
        const deviceAlerts = alerts.filter(alert =>
            alert.device_name === selectedDevice &&
            isValid(startTime) && isValid(endTime) &&
            new Date(alert.time) >= startTime &&
            new Date(alert.time) <= endTime
        );

        const alertAnnotations = deviceAlerts.map((alert) => {
            const isWarning = alert.severity.toLowerCase() === 'warning';
            const alertTimeValue = new Date(alert.time).valueOf();

            return {
                type: 'point',
                xValue: alertTimeValue,
                yValue: (ctx) => {
                    const chart = ctx.chart;
                    if (!chart || !chart.scales?.y?.max) return 0;
                    const datasets = chart.data.datasets || [];
                    let y = null;
                    const targetDatasetIndex = datasets.findIndex(ds =>
                       alert.param_name && ds.label?.toLowerCase().includes(alert.param_name.replace(/_/g, ' ').toLowerCase())
                    );
                    if (targetDatasetIndex !== -1) {
                        const targetDataset = datasets[targetDatasetIndex];
                        let closestPoint = null;
                        let minDiff = Infinity;
                        (targetDataset.data || []).forEach(point => {
                            if (point && typeof point.x === 'number') {
                                const diff = Math.abs(point.x - alertTimeValue);
                                if (diff < minDiff) {
                                    minDiff = diff;
                                    closestPoint = point;
                                }
                            }
                        });
                        if (closestPoint && minDiff < 60 * 1000 * 5) {
                             y = closestPoint.y;
                        }
                    }
                    const maxY = chart.scales.y.max;
                    return y !== null ? y : maxY + (maxY * 0.05);
                },
                backgroundColor: isWarning ? 'rgba(240, 173, 78, 0.7)' : 'rgba(217, 83, 79, 0.7)',
                borderColor: isWarning ? '#f0ad4e' : '#d9534f',
                borderWidth: 1, radius: 6, pointStyle: 'triangle', rotation: 180, display: true,
            };
        });

        const minTime = isValid(startTime) ? startTime.valueOf() : getDefaultStartTime().valueOf();
        const maxTime = isValid(endTime) ? endTime.valueOf() : getDefaultEndTime().valueOf();

        return {
            responsive: true, maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: { labels: { color: '#1e2a3b' } },
                tooltip: {
                    callbacks: {
                        title: function (tooltipItems) {
                            if (tooltipItems[0]?.parsed?.x) { return new Date(tooltipItems[0].parsed.x).toLocaleString(); }
                            return '';
                        }
                    }
                },
                annotation: { annotations: alertAnnotations }
            },
            scales: {
                y: { beginAtZero: false, ticks: { color: '#5a687d' }, grid: { color: '#e6e9f0' } },
                x: {
                    type: 'time', min: minTime, max: maxTime,
                    ticks: { color: '#5a687d', autoSkip: true, maxTicksLimit: 20, source: 'auto' },
                    grid: { display: false },
                    time: {
                        unit: 'minute', tooltipFormat: 'YYYY-MM-DD HH:mm:ss',
                        displayFormats: { millisecond: 'HH:mm:ss.SSS', second: 'HH:mm:ss', minute: 'HH:mm', hour: 'HH:mm', day: 'MMM d', week: 'll', month: 'MMM YYYY', year: 'YYYY', }
                    }
                }
            },
            animation: { duration: 0 },
            elements: { line: { spanGaps: true, tension: 0.1 }, point: { radius: 0, hoverRadius: 5, hitRadius: 10 } }
        };
    }, [alerts, selectedDevice, startTime, endTime]);

    // --- Data Fetching ---
    const fetchData = useCallback(async (isInitialLoad = false) => {
        const currentStartTime = isValid(startTime) ? startTime : getDefaultStartTime();
        const currentEndTime = isValid(endTime) ? endTime : getDefaultEndTime();
        if (!selectedDevice) { if (isInitialLoad) setIsLoading(false); return; }
        setIsLoading(true);
        const startTimeISO = currentStartTime.toISOString();
        const endTimeISO = currentEndTime.toISOString();
        const analyticsUrl = `${API_BASE_URL}/devices/${selectedDevice}/analytics?start_time=${startTimeISO}&end_time=${endTimeISO}`;
        const alertsUrl = `${API_BASE_URL}/alerts?start_time=${startTimeISO}&end_time=${endTimeISO}&limit=500`;
        console.log("Fetching analytics:", analyticsUrl);
        console.log("Fetching alerts:", alertsUrl);
        try {
            const [deviceRes, alertsRes] = await Promise.all([ axios.get(analyticsUrl), axios.get(alertsUrl) ]);
            console.log("API Response Data:", deviceRes.data);
            const rawDatasets = deviceRes.data.trends?.datasets || [];
            const newTrendsData = {
                datasets: rawDatasets.map((ds, i) => {
                    const validDataPoints = (ds.data || [])
                        .map(d => { const timestamp = new Date(d.x).valueOf(); const value = parseFloat(d.y); return (!isNaN(timestamp) && !isNaN(value)) ? { x: timestamp, y: value } : null; })
                        .filter(point => point !== null);
                    return {
                        label: ds.label || `Dataset ${i+1}`, data: validDataPoints,
                        borderColor: chartColors[i % chartColors.length].border, backgroundColor: chartColors[i % chartColors.length].bg,
                        fill: true, tension: 0.1, borderWidth: 1.5, pointRadius: 0, pointHoverRadius: 5, pointHitRadius: 10, spanGaps: true,
                    };
                })
            };
            setDashboardData({
                latest_metrics: deviceRes.data.latest_metrics || {}, trends: newTrendsData,
                daily_averages_table: deviceRes.data.daily_averages_table || [], overall_period_averages: deviceRes.data.overall_period_averages || {}
            });
            setAlerts(alertsRes.data || []);
            setRefreshKey(oldKey => oldKey + 1);
        } catch (error) {
            console.error(`Error fetching data for ${selectedDevice}:`, error);
             if (error.response) { console.error("Error response data:", error.response.data); console.error("Error response status:", error.response.status); }
             else if (error.request) { console.error("Error request made but no response received:", error.request); }
             else { console.error('Error setting up request:', error.message); }
             setDashboardData({ latest_metrics: {}, trends: { datasets: [] }, daily_averages_table: [], overall_period_averages: {} });
            setAlerts([]);
        } finally { setIsLoading(false); }
    }, [selectedDevice, startTime, endTime]);

    // --- Effects ---
    useEffect(() => {
        const fetchDeviceList = async () => {
             setIsLoading(true);
            try {
                const res = await axios.get(`${API_BASE_URL}/devices`); setDevices(res.data || {});
                 const firstDevice = Object.values(res.data || {})[0]?.[0];
                if (firstDevice) { setSelectedDevice(firstDevice); }
                else { setIsLoading(false); setDashboardData({ latest_metrics: {}, trends: { datasets: [] }, daily_averages_table: [], overall_period_averages: {} }); setAlerts([]); }
            } catch (error) { console.error("Error fetching device list:", error); setIsLoading(false); }
        };
        fetchDeviceList();
    }, []);

    useEffect(() => {
        if (selectedDevice && isValid(startTime) && isValid(endTime)) {
             const timerId = setTimeout(() => fetchData(true), 0);
             return () => clearTimeout(timerId);
        } else if (selectedDevice && (!isValid(startTime) || !isValid(endTime))) {
            console.warn("Invalid date range detected in effect, resetting to default.");
            const timerId = setTimeout(() => { setStartTime(getDefaultStartTime()); setEndTime(getDefaultEndTime()); }, 0);
             return () => clearTimeout(timerId);
        }
     }, [selectedDevice, startTime, endTime]); // Removed fetchData from deps

    // --- Helper to format local date/time ---
    const formatDateTimeLocal = (date) => {
        if (!date || !isValid(date)) return '';
        try { const adjustedDate = new Date(date.getTime() - date.getTimezoneOffset() * 60000); return adjustedDate.toISOString().slice(0, 16); }
        catch (e) { console.error("Error formatting date:", date, e); return ''; }
    };

    // --- Pivoted Data for Tables (Memoized) ---
    const pivotedDailyAverages = useMemo(() => {
        if (!dashboardData.daily_averages_table || dashboardData.daily_averages_table.length === 0) return { dates: [], params: [], dataMap: {} };
        try {
            const dates = [...new Set(dashboardData.daily_averages_table.map(([date]) => new Date(date).toLocaleDateString()))].sort((a, b) => new Date(b) - new Date(a));
            const params = [...new Set(dashboardData.daily_averages_table.map(([, name]) => name.replace(/_/g, ' ')))].sort();
            const dataMap = dashboardData.daily_averages_table.reduce((acc, [date, name, avg]) => {
                const dateKey = new Date(date).toLocaleDateString(); const paramKey = name.replace(/_/g, ' '); if (!acc[dateKey]) acc[dateKey] = {}; acc[dateKey][paramKey] = Number(avg).toFixed(2); return acc;
            }, {});
            return { dates, params, dataMap };
        } catch (e) { console.error("Error processing daily averages:", e); return { dates: [], params: [], dataMap: {} }; }
    }, [dashboardData.daily_averages_table]);

    // --- NEW: Handler for clicking on a device in the alerts table ---
    const handleAlertDeviceClick = (deviceName) => {
        // Check if the clicked device exists in our list
        const deviceExists = Object.values(devices).flat().includes(deviceName);
        if (deviceExists && deviceName !== selectedDevice) {
            console.log(`Switching dashboard to device: ${deviceName}`);
            setSelectedDevice(deviceName);
            // Optional: scroll to top
            // window.scrollTo(0, 0);
        } else if (!deviceExists) {
            console.warn(`Device ${deviceName} from alert not found in the device list.`);
        }
    };


    // --- Render ---
    return (
        <div className="dashboard-layout">
            <aside className="sidebar">
                <div className="sidebar-header"><h2>DEVICES</h2></div>
                {Object.keys(devices).length === 0 && !isLoading && <p>No devices found.</p>}
                {Object.entries(devices).map(([type, list]) => (
                    <div key={type} className="device-group">
                        <h3>{type} ({list.length})</h3>
                        <select onChange={e => setSelectedDevice(e.target.value)} value={list.includes(selectedDevice) ? selectedDevice : ''} aria-label={`Select ${type} device`}>
                             <option value="" disabled>Select a {type} device</option> {list.map(d => <option key={d} value={d}>{d}</option>)}
                        </select>
                    </div>
                ))}
                 <div className="time-range-picker device-group">
                    <h3>Time Range</h3>
                    <div><label htmlFor="start-time">Start:</label><input id="start-time" type="datetime-local" value={formatDateTimeLocal(startTime)} onChange={handleStartTimeChange} max={formatDateTimeLocal(endTime)} /></div>
                    <div><label htmlFor="end-time">End:</label><input id="end-time" type="datetime-local" value={formatDateTimeLocal(endTime)} onChange={handleEndTimeChange} min={formatDateTimeLocal(startTime)} /></div>
                 </div>
            </aside>
            <header className="main-header">
                 <h1>{selectedDevice ? `Dashboard for ${selectedDevice}` : "Select a Device"}</h1>
                 <button onClick={() => fetchData(false)} disabled={isLoading || !selectedDevice}>{isLoading ? 'Refreshing...' : 'Refresh Data'}</button>
            </header>
            <main className="main-content">
                {!selectedDevice && !isLoading && <p className="loading-text">Please select a device from the sidebar.</p>}
                {isLoading && <div className="loading-text">Loading data...</div>}
                 {!isLoading && selectedDevice && (
                    <>
                        <section className="data-section">
                            <h3>Live Metrics (Latest)</h3>
                            <div className="metrics-grid">
                                {Object.keys(dashboardData.latest_metrics).length > 0 ? Object.entries(dashboardData.latest_metrics).map(([name, value]) => ( <div key={name} className="metric-card"><h4>{name.replace(/_/g, ' ')}</h4><p>{value}</p></div> )) : <p>No latest metrics available.</p>}
                            </div>
                        </section>
                        <section className="data-section">
                            <h3>Trends ({isValid(startTime) ? startTime.toLocaleString() : '...'} - {isValid(endTime) ? endTime.toLocaleString() : '...'})</h3>
                            <div className="chart-container">
                                {isValid(startTime) && isValid(endTime) && dashboardData.trends?.datasets?.length > 0 && dashboardData.trends.datasets.some(ds => ds.data.length > 0) ? ( <Line key={refreshKey} options={chartOptions} data={dashboardData.trends} redraw={true} /> ) : <p>No trend data available for the selected period.</p>}
                            </div>
                        </section>
                        <section className="data-section">
                            <h3>Daily Averages (Max 7 days in range)</h3>
                            <div className="table-container">
                                {pivotedDailyAverages.dates.length > 0 ? ( <table><thead><tr><th>Date</th>{pivotedDailyAverages.params.map(param => <th key={param}>{param}</th>)}</tr></thead><tbody>{pivotedDailyAverages.dates.map(date => ( <tr key={date}><td>{date}</td>{pivotedDailyAverages.params.map(param => ( <td key={param}>{pivotedDailyAverages.dataMap[date]?.[param] || '-'}</td> ))}</tr> ))}</tbody></table> ) : <p>No daily average data available.</p>}
                            </div>
                        </section>
                        <section className="data-section">
                            <h3>Overall Averages ({isValid(startTime) ? startTime.toLocaleDateString() : '...'} - {isValid(endTime) ? endTime.toLocaleDateString() : '...'})</h3>
                            <div className="table-container">
                                {Object.keys(dashboardData.overall_period_averages).length > 0 ? ( <table><thead><tr><th>Parameter</th><th>Average Value</th></tr></thead><tbody>{Object.entries(dashboardData.overall_period_averages).map(([name, value]) => ( <tr key={name}><td>{name.replace(/_/g, ' ')}</td><td>{value}</td></tr> ))}</tbody></table> ) : <p>No overall average data available for the period.</p>}
                            </div>
                        </section>
                        {/* Alerts Table Section - MODIFIED */}
                        <section className="data-section">
                            <h3>Alerts in Range ({alerts.length})</h3>
                            <div className="table-container">
                                {alerts.length > 0 ? (
                                    <table>
                                        <thead><tr><th>Time</th><th>Device</th><th>Message</th><th>Severity</th></tr></thead>
                                        <tbody>
                                            {alerts.map((alert) => (
                                                <tr key={alert.id}>
                                                    <td>{new Date(alert.time).toLocaleString()}</td>
                                                    {/* Make the device name cell clickable */}
                                                    <td
                                                        onClick={() => handleAlertDeviceClick(alert.device_name)}
                                                        style={{ cursor: 'pointer', color: 'var(--accent-color)', textDecoration: 'underline' }} // Add styles for clickability
                                                        title={`Click to view ${alert.device_name}`} // Add tooltip
                                                    >
                                                        {alert.device_name}
                                                    </td>
                                                    <td>{alert.message}</td>
                                                    <td className={`severity-${alert.severity.toLowerCase()}`}>{alert.severity}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                ) : <p>No alerts in the selected time range.</p>}
                            </div>
                        </section>
                    </>
                 )}
            </main>
        </div>
    );
};

export default App;