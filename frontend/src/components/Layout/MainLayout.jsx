import React from 'react';
import { useTranslation } from 'react-i18next';
import Sidebar from './Sidebar';
import Header from './Header';

const MainLayout = ({ children, onLogout }) => {
    const { t } = useTranslation();
    const isRTL = document.documentElement.dir === 'rtl';

    return (
        <div className="app-container">
            <Sidebar onLogout={onLogout} />
            <div className="main-content">
                <Header />
                <main className="content-area">
                    {children}
                </main>
                <footer className="footer">
                    <div className={`flex items-center ${isRTL ? 'space-x-reverse space-x-2' : 'space-x-2'}`}>
                        <span className="text-slate-400">{t('footer.poweredBy')}</span>
                        <span className="font-bold text-red-800">Scalovate</span>
                        <span className="text-slate-300">|</span>
                        <span className="font-bold text-red-600">Red Hat</span>
                    </div>
                    <div className="text-slate-400">
                        {t('footer.copyright')}
                    </div>
                </footer>
            </div>
        </div>
    );
};

export default MainLayout;
