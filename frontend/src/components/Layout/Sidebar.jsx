import React from 'react';
import { NavLink } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
    Squares2X2Icon,
    LightBulbIcon,
    DocumentTextIcon,
    Cog6ToothIcon,
    ChatBubbleLeftRightIcon,
    FolderIcon,
    ChartBarIcon,
    ScaleIcon,
    ShieldCheckIcon
} from '@heroicons/react/24/outline';

const Sidebar = ({ onLogout }) => {
    const { t } = useTranslation();
    const username = localStorage.getItem('username');
    const isRTL = document.documentElement.dir === 'rtl';
    
    const menuItems = [
        { name: t('common.dashboard'), icon: Squares2X2Icon, path: '/' },
        { name: t('common.intelligence'), icon: LightBulbIcon, path: '/intelligence' },
        { name: t('common.comparison'), icon: ScaleIcon, path: '/comparison' },
        { name: t('common.caseChat'), icon: ChatBubbleLeftRightIcon, path: '/chat' },
        { name: t('common.adminConsole'), icon: ShieldCheckIcon, path: '/admin' },
        { name: t('common.reports'), icon: DocumentTextIcon, path: '/reports' },
        { name: t('common.settings'), icon: Cog6ToothIcon, path: '/settings' },
    ];

    const collections = [
        { name: t('sidebar.allLegalCases'), icon: FolderIcon },
        { name: t('sidebar.recentComparisons'), icon: FolderIcon },
        { name: t('sidebar.legalPrecedents'), icon: ScaleIcon },
        { name: t('sidebar.patternTrends'), icon: ChartBarIcon },
    ];

    return (
        <div className="sidebar">
            <div className="p-6">
                <div className="flex items-center space-x-2 mb-8">
                    <div className="w-8 h-8 bg-black rounded flex items-center justify-center">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
                        </svg>
                    </div>
                    <span className="text-xl font-bold">Scalovate PoC</span>
                </div>

                <nav className="space-y-1">
                    <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 px-3">{t('sidebar.menu')}</p>
                    {menuItems.map((item) => (
                        <NavLink
                            key={item.path}
                            to={item.path}
                            className={({ isActive }) =>
                                `flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${isActive
                                    ? 'bg-red-50 text-red-700'
                                    : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                                }`}
                        >
                            <item.icon className={`${isRTL ? 'ml-3' : 'mr-3'} h-5 w-5 flex-shrink-0`} aria-hidden="true" />
                            {item.name}
                        </NavLink>
                    ))}
                </nav>

                <div className="mt-8">
                    <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 px-3">{t('sidebar.collections')}</p>
                    <div className="space-y-1">
                        {collections.map((item) => (
                            <div key={item.name} className="flex items-center px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50 rounded-md cursor-pointer">
                                <item.icon className={`${isRTL ? 'ml-3' : 'mr-3'} h-5 w-5 flex-shrink-0 text-slate-400`} aria-hidden="true" />
                                {item.name}
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            <div className="mt-auto p-6 border-t border-slate-100 flex flex-col space-y-4">
                <div className="flex items-center space-x-3 px-3">
                    <div className="w-8 h-8 rounded-lg bg-teal-100 flex items-center justify-center text-teal-600 font-bold text-xs uppercase">
                        {localStorage.getItem('username')?.[0]}
                    </div>
                    <div className="flex-grow overflow-hidden">
                        <div className="text-xs font-bold text-slate-800 truncate">{localStorage.getItem('username')}</div>
                        <div className="text-[10px] text-slate-400">{t('sidebar.standardAccess')}</div>
                    </div>
                </div>
                <button
                    onClick={onLogout}
                    className={`w-full py-2 bg-slate-50 border border-slate-200 text-xs font-bold rounded-lg hover:bg-slate-100 flex items-center justify-center ${isRTL ? 'space-x-reverse' : 'space-x-2'}`}
                >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" /></svg>
                    <span>{t('common.signOut')}</span>
                </button>
            </div>
        </div>
    );
};

export default Sidebar;
