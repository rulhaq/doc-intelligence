import React from 'react';
import { useTranslation } from 'react-i18next';
import {
    Squares2X2Icon,
    LightBulbIcon,
    DocumentTextIcon,
    ScaleIcon,
    ChatBubbleLeftRightIcon,
    ArrowRightIcon
} from '@heroicons/react/24/outline';
import { Link } from 'react-router-dom';

const Dashboard = () => {
    const { t } = useTranslation();
    const isRTL = document.documentElement.dir === 'rtl';
    
    const stats = [
        { name: t('dashboard.totalCasesAnalyzed'), value: '142', icon: Squares2X2Icon, color: 'text-blue-600', bg: 'bg-blue-50' },
        { name: t('dashboard.activeIntelligentInsights'), value: '12', icon: LightBulbIcon, color: 'text-red-700', bg: 'bg-red-50' },
        { name: t('dashboard.precedentsFound'), value: '458', icon: ScaleIcon, color: 'text-teal-600', bg: 'bg-teal-50' },
        { name: t('dashboard.reportsGenerated'), value: '28', icon: DocumentTextIcon, color: 'text-purple-600', bg: 'bg-purple-50' },
    ];

    const recentActivities = [
        { title: 'Project Alpha Due Diligence', type: 'Intelligence Analysis', time: '2 hours ago', status: 'Completed' },
        { title: 'MSA Liability Review', type: 'Case Chat', time: '5 hours ago', status: 'In Progress' },
        { title: 'Global Logistics vs Nordic', type: 'Case Comparison', time: 'Yesterday', status: 'Saved' },
        { title: 'Standard Compliance Audit', type: 'Report Generation', time: '2 days ago', status: 'Completed' },
    ];

    return (
        <div className="space-y-8">
            <div>
                <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">{t('dashboard.title')}</h1>
                <p className="text-sm text-slate-500 mt-1">{t('dashboard.subtitle')}</p>
            </div>

            <div className="grid grid-cols-4 gap-6">
                {stats.map((stat) => (
                    <div key={stat.name} className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm">
                        <div className={`p-3 rounded-xl ${stat.bg} w-fit mb-4`}>
                            <stat.icon className={`h-6 w-6 ${stat.color}`} />
                        </div>
                        <div className="text-2xl font-bold text-slate-900">{stat.value}</div>
                        <div className="text-xs font-bold text-slate-400 uppercase mt-1">{stat.name}</div>
                    </div>
                ))}
            </div>

            <div className="grid grid-cols-3 gap-8">
                <div className="col-span-2 bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
                    <div className={`p-6 border-b border-slate-50 flex justify-between items-center`}>
                        <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide">{t('dashboard.recentActivities')}</h3>
                        <button className={`text-xs font-bold text-red-800 hover:underline flex items-center ${isRTL ? 'space-x-reverse space-x-1' : 'space-x-1'}`}>
                            <span>{t('common.viewAll')}</span>
                            <ArrowRightIcon className={`h-3 w-3 ${isRTL ? 'rotate-180' : ''}`} />
                        </button>
                    </div>
                    <div className="divide-y divide-slate-50">
                        {recentActivities.map((activity, i) => (
                            <div key={i} className="p-6 flex items-center justify-between hover:bg-slate-50 transition-colors">
                                <div className="flex items-center space-x-4">
                                    <div className="w-10 h-10 rounded-full bg-slate-50 flex items-center justify-center text-slate-400">
                                        {activity.type === 'Intelligence Analysis' && <LightBulbIcon className="h-5 w-5" />}
                                        {activity.type === 'Case Chat' && <ChatBubbleLeftRightIcon className="h-5 w-5" />}
                                        {activity.type === 'Case Comparison' && <ScaleIcon className="h-5 w-5" />}
                                        {activity.type === 'Report Generation' && <DocumentTextIcon className="h-5 w-5" />}
                                    </div>
                                    <div>
                                        <div className="text-sm font-bold text-slate-900">{activity.title}</div>
                                        <div className="text-[10px] font-bold text-slate-400 uppercase">{activity.type}</div>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <div className="text-xs font-bold text-slate-900">{activity.status}</div>
                                    <div className="text-[10px] text-slate-400">{activity.time}</div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="space-y-6">
                    <div className={`bg-red-900 rounded-2xl p-6 text-white shadow-xl shadow-red-900/20 relative overflow-hidden group`}>
                        <div className={`absolute top-0 ${isRTL ? 'left-0' : 'right-0'} p-4 opacity-10 group-hover:rotate-12 transition-transform`}>
                            <ScaleIcon className="h-24 w-24" />
                        </div>
                        <h3 className="text-lg font-bold mb-2">{t('dashboard.newComparison')}</h3>
                        <p className="text-xs text-red-100/70 mb-6 leading-relaxed">{t('dashboard.newComparisonDesc')}</p>
                        <Link to="/comparison" className="bg-white text-red-950 px-4 py-2 rounded-xl text-xs font-bold inline-block shadow-lg hover:bg-red-50 transition-colors">{t('dashboard.startAnalysis')}</Link>
                    </div>

                    <div className={`bg-slate-900 rounded-2xl p-6 text-white shadow-xl shadow-slate-900/20 relative overflow-hidden group`}>
                        <div className={`absolute top-0 ${isRTL ? 'left-0' : 'right-0'} p-4 opacity-10 group-hover:-rotate-12 transition-transform`}>
                            <ChatBubbleLeftRightIcon className="h-24 w-24" />
                        </div>
                        <h3 className="text-lg font-bold mb-2">{t('dashboard.legalAIAssistant')}</h3>
                        <p className="text-xs text-slate-400 mb-6 leading-relaxed">{t('dashboard.legalAIAssistantDesc')}</p>
                        <Link to="/chat" className="bg-red-800 text-white px-4 py-2 rounded-xl text-xs font-bold inline-block shadow-lg hover:bg-red-900 transition-colors">{t('dashboard.openChat')}</Link>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
