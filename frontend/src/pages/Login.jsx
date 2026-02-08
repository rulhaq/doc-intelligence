import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { api } from '../services/api';
import LanguageSwitcher from '../components/LanguageSwitcher';

const Login = ({ onLogin }) => {
    const { t } = useTranslation();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();
    const isRTL = document.documentElement.dir === 'rtl';

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            const formData = new FormData();
            formData.append('username', username);
            formData.append('password', password);

            const response = await api.post('/login', formData);
            const { access_token } = response.data;

            localStorage.setItem('token', access_token);
            localStorage.setItem('username', username);

            onLogin(access_token);
            navigate('/');
        } catch (err) {
            setError(t('login.incorrectCredentials'));
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-slate-50 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-md w-full space-y-8 bg-white p-10 rounded-2xl shadow-xl border border-slate-100">
                <div className="absolute top-4 right-4">
                    <LanguageSwitcher />
                </div>
                <div>
                    <div className="flex justify-center flex-col items-center">
                        <div className="w-12 h-12 bg-red-900 rounded-xl flex items-center justify-center text-white shadow-lg mb-4">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
                            </svg>
                        </div>
                        <h2 className="text-center text-3xl font-extrabold text-slate-900 tracking-tight">
                            Scalovate Intelligence
                        </h2>
                        <p className="mt-2 text-center text-sm text-slate-400">
                            {t('login.title')}
                        </p>
                    </div>
                </div>
                <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
                    <div className="rounded-md shadow-sm -space-y-px">
                        <div>
                            <input
                                type="text"
                                required
                                className={`appearance-none ${isRTL ? 'rounded-b-xl' : 'rounded-t-xl'} relative block w-full px-4 py-3 border border-slate-200 placeholder-slate-400 text-slate-900 focus:outline-none focus:ring-red-900 focus:border-red-900 focus:z-10 sm:text-sm`}
                                placeholder={t('login.username')}
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                dir={isRTL ? 'rtl' : 'ltr'}
                            />
                        </div>
                        <div>
                            <input
                                type="password"
                                required
                                className={`appearance-none ${isRTL ? 'rounded-t-xl' : 'rounded-b-xl'} relative block w-full px-4 py-3 border border-slate-200 placeholder-slate-400 text-slate-900 focus:outline-none focus:ring-red-900 focus:border-red-900 focus:z-10 sm:text-sm`}
                                placeholder={t('login.password')}
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                dir={isRTL ? 'rtl' : 'ltr'}
                            />
                        </div>
                    </div>

                    {error && (
                        <div className="text-red-600 text-sm text-center font-medium bg-red-50 p-2 rounded-lg">
                            {error}
                        </div>
                    )}

                    <div>
                        <button
                            type="submit"
                            disabled={loading}
                            className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-bold rounded-xl text-white bg-red-950 hover:bg-black focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-900 transition-all shadow-lg shadow-red-900/10 disabled:opacity-50"
                        >
                            {loading ? t('common.loading') : t('login.login')}
                        </button>
                    </div>
                </form>

                <div className="mt-6 text-center border-t border-slate-50 pt-6">
                    <div className="flex items-center justify-center space-x-2 grayscale opacity-50">
                        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Powered by</span>
                        <span className="text-xs font-bold text-slate-800">Scalovate</span>
                        <span className="text-slate-300">|</span>
                        <span className="text-xs font-bold text-red-600">Red Hat</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Login;
