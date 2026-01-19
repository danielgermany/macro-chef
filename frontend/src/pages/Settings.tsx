import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { userService } from '../services/userService';
import { useAuth } from '../contexts/AuthContext';
import { useUser } from '../hooks/useUser';
import { useToast } from '../contexts/ToastContext';
import { exportBodyMetrics } from '../utils/export';
import { User, Settings as SettingsIcon, Target, TrendingUp, Save, Plus, Download, Lock, Mail } from 'lucide-react';
import { format, parseISO } from 'date-fns';
import type { User as UserType, BodyMetrics, ProgressSummary } from '../types/user';

const GOAL_TYPES = ['bulk', 'cut', 'maintain', 'recomp'] as const;
const ACTIVITY_LEVELS = ['sedentary', 'light', 'moderate', 'very_active', 'athlete'] as const;
const COOKING_SKILLS = ['beginner', 'intermediate', 'advanced'] as const;
const COMMON_EQUIPMENT = ['oven', 'stovetop', 'microwave', 'air_fryer', 'slow_cooker', 'blender', 'food_processor'];

export function Settings() {
  const { user: authUser } = useAuth();
  const userId = authUser?.id || 1;
  const { data: user, isLoading: isLoadingUser } = useUser(userId);
  const { showSuccess, showError } = useToast();
  const queryClient = useQueryClient();

  const [activeTab, setActiveTab] = useState<'profile' | 'metrics' | 'preferences' | 'security'>('profile');
  const [showMetricsForm, setShowMetricsForm] = useState(false);

  // Profile update mutation
  const updateUserMutation = useMutation({
    mutationFn: (data: Partial<UserType>) => userService.updateUser(userId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user', userId] });
      showSuccess('Profile updated successfully!');
    },
    onError: () => {
      showError('Failed to update profile');
    },
  });

  // Body metrics mutations
  const logMetricsMutation = useMutation({
    mutationFn: (metrics: Partial<BodyMetrics>) => userService.logBodyMetrics(userId, metrics),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['metrics', userId] });
      queryClient.invalidateQueries({ queryKey: ['progress', userId] });
      setShowMetricsForm(false);
      showSuccess('Body metrics logged successfully!');
    },
    onError: () => {
      showError('Failed to log body metrics');
    },
  });

  // Fetch metrics history
  const { data: metricsHistory } = useQuery({
    queryKey: ['metrics', userId],
    queryFn: () => userService.getMetricsHistory(userId, 90),
  });

  // Fetch progress summary
  const { data: progressSummary } = useQuery({
    queryKey: ['progress', userId],
    queryFn: () => userService.getProgressSummary(userId, 30),
  });

  // Profile form state
  const [profileForm, setProfileForm] = useState<Partial<UserType>>({});

  // Metrics form state
  const [metricsForm, setMetricsForm] = useState<Partial<BodyMetrics>>({
    measurement_date: format(new Date(), 'yyyy-MM-dd'),
  });

  // Security form state
  const [passwordForm, setPasswordForm] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });
  const [emailForm, setEmailForm] = useState({
    newEmail: '',
    password: '',
  });

  // Password change mutation
  const changePasswordMutation = useMutation({
    mutationFn: () => userService.changePassword(
      passwordForm.currentPassword,
      passwordForm.newPassword,
      passwordForm.confirmPassword
    ),
    onSuccess: () => {
      setPasswordForm({ currentPassword: '', newPassword: '', confirmPassword: '' });
      showSuccess('Password changed successfully!');
    },
    onError: (error: any) => {
      showError(error.response?.data?.detail || 'Failed to change password');
    },
  });

  // Email change mutation
  const changeEmailMutation = useMutation({
    mutationFn: () => userService.changeEmail(emailForm.newEmail, emailForm.password),
    onSuccess: () => {
      setEmailForm({ newEmail: '', password: '' });
      queryClient.invalidateQueries({ queryKey: ['user', userId] });
      showSuccess('Email changed successfully!');
    },
    onError: (error: any) => {
      showError(error.response?.data?.detail || 'Failed to change email');
    },
  });

  if (isLoadingUser) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-pulse text-gray-500">Loading settings...</div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="bg-white rounded-xl shadow-sm p-12 text-center">
        <SettingsIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h2 className="text-xl font-semibold mb-2">User Not Found</h2>
        <p className="text-gray-500">Unable to load user profile.</p>
      </div>
    );
  }

  // Initialize form with user data
  const handleProfileSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    updateUserMutation.mutate(profileForm);
  };

  const handleMetricsSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    logMetricsMutation.mutate(metricsForm);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-500 mt-1">Manage your profile, preferences, and body metrics</p>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-xl shadow-sm">
        <div className="border-b border-gray-200">
          <nav className="flex -mb-px">
            <button
              onClick={() => setActiveTab('profile')}
              className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'profile'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <User className="w-5 h-5 inline mr-2" />
              Profile
            </button>
            <button
              onClick={() => setActiveTab('metrics')}
              className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'metrics'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Target className="w-5 h-5 inline mr-2" />
              Body Metrics
            </button>
            <button
              onClick={() => setActiveTab('preferences')}
              className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'preferences'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <SettingsIcon className="w-5 h-5 inline mr-2" />
              Preferences
            </button>
            <button
              onClick={() => setActiveTab('security')}
              className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'security'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Lock className="w-5 h-5 inline mr-2" />
              Security
            </button>
          </nav>
        </div>

        <div className="p-6">
          {/* Profile Tab */}
          {activeTab === 'profile' && (
            <div className="space-y-6">
              <h2 className="text-xl font-semibold">Profile Information</h2>
              <form onSubmit={handleProfileSubmit} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Name
                    </label>
                    <input
                      type="text"
                      defaultValue={user.name}
                      onChange={(e) => setProfileForm({ ...profileForm, name: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Age
                    </label>
                    <input
                      type="number"
                      min="13"
                      max="120"
                      defaultValue={user.age}
                      onChange={(e) => setProfileForm({ ...profileForm, age: parseInt(e.target.value) })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Height (inches)
                    </label>
                    <input
                      type="number"
                      step="0.1"
                      min="0"
                      defaultValue={user.height_inches}
                      onChange={(e) => setProfileForm({ ...profileForm, height_inches: parseFloat(e.target.value) })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Weight (lbs)
                    </label>
                    <input
                      type="number"
                      step="0.1"
                      min="0"
                      defaultValue={user.weight_lbs}
                      onChange={(e) => setProfileForm({ ...profileForm, weight_lbs: parseFloat(e.target.value) })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Goal Type
                    </label>
                    <select
                      defaultValue={user.goal_type}
                      onChange={(e) => setProfileForm({ ...profileForm, goal_type: e.target.value as any })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    >
                      {GOAL_TYPES.map((goal) => (
                        <option key={goal} value={goal}>
                          {goal.charAt(0).toUpperCase() + goal.slice(1)}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Activity Level
                    </label>
                    <select
                      defaultValue={user.activity_level}
                      onChange={(e) => setProfileForm({ ...profileForm, activity_level: e.target.value as any })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    >
                      {ACTIVITY_LEVELS.map((level) => (
                        <option key={level} value={level}>
                          {level.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Training Days per Week
                    </label>
                    <input
                      type="number"
                      min="0"
                      max="7"
                      defaultValue={user.training_days_per_week}
                      onChange={(e) => setProfileForm({ ...profileForm, training_days_per_week: parseInt(e.target.value) })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Weekly Budget ($)
                    </label>
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      defaultValue={user.weekly_budget_usd}
                      onChange={(e) => setProfileForm({ ...profileForm, weekly_budget_usd: parseFloat(e.target.value) })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                  </div>
                </div>
                <div className="flex justify-end">
                  <button
                    type="submit"
                    disabled={updateUserMutation.isPending}
                    className="flex items-center gap-2 px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors"
                  >
                    <Save className="w-5 h-5" />
                    {updateUserMutation.isPending ? 'Saving...' : 'Save Changes'}
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* Body Metrics Tab */}
          {activeTab === 'metrics' && (
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold">Body Metrics</h2>
                <button
                  onClick={() => setShowMetricsForm(!showMetricsForm)}
                  className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
                >
                  <Plus className="w-5 h-5" />
                  Log Metrics
                </button>
              </div>

              {/* Progress Summary */}
              {progressSummary && progressSummary.status === 'success' && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <TrendingUp className="w-5 h-5 text-blue-600" />
                    <h3 className="font-semibold text-blue-900">Progress Summary (Last 30 Days)</h3>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    {progressSummary.weight_change_lbs !== null && (
                      <div>
                        <div className="text-blue-600 font-medium">Weight Change</div>
                        <div className="text-lg font-bold">
                          {progressSummary.weight_change_lbs > 0 ? '+' : ''}
                          {progressSummary.weight_change_lbs?.toFixed(1)} lbs
                        </div>
                      </div>
                    )}
                    {progressSummary.muscle_change_lbs !== null && (
                      <div>
                        <div className="text-blue-600 font-medium">Muscle Change</div>
                        <div className="text-lg font-bold">
                          {progressSummary.muscle_change_lbs > 0 ? '+' : ''}
                          {progressSummary.muscle_change_lbs?.toFixed(1)} lbs
                        </div>
                      </div>
                    )}
                    {progressSummary.current_weight !== null && (
                      <div>
                        <div className="text-blue-600 font-medium">Current Weight</div>
                        <div className="text-lg font-bold">{progressSummary.current_weight.toFixed(1)} lbs</div>
                      </div>
                    )}
                    {progressSummary.current_bodyfat !== null && (
                      <div>
                        <div className="text-blue-600 font-medium">Body Fat %</div>
                        <div className="text-lg font-bold">{progressSummary.current_bodyfat.toFixed(1)}%</div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Log Metrics Form */}
              {showMetricsForm && (
                <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
                  <h3 className="text-lg font-semibold mb-4">Log New Body Metrics</h3>
                  <form onSubmit={handleMetricsSubmit} className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Weight (lbs) *
                        </label>
                        <input
                          type="number"
                          step="0.1"
                          min="0"
                          required
                          value={metricsForm.weight_lbs || ''}
                          onChange={(e) => setMetricsForm({ ...metricsForm, weight_lbs: parseFloat(e.target.value) })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Body Fat %
                        </label>
                        <input
                          type="number"
                          step="0.1"
                          min="1"
                          max="60"
                          value={metricsForm.body_fat_pct || ''}
                          onChange={(e) => setMetricsForm({ ...metricsForm, body_fat_pct: parseFloat(e.target.value) })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Waist (inches)
                        </label>
                        <input
                          type="number"
                          step="0.1"
                          min="0"
                          value={metricsForm.waist_inches || ''}
                          onChange={(e) => setMetricsForm({ ...metricsForm, waist_inches: parseFloat(e.target.value) })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Chest (inches)
                        </label>
                        <input
                          type="number"
                          step="0.1"
                          min="0"
                          value={metricsForm.chest_inches || ''}
                          onChange={(e) => setMetricsForm({ ...metricsForm, chest_inches: parseFloat(e.target.value) })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Arms (inches)
                        </label>
                        <input
                          type="number"
                          step="0.1"
                          min="0"
                          value={metricsForm.arms_inches || ''}
                          onChange={(e) => setMetricsForm({ ...metricsForm, arms_inches: parseFloat(e.target.value) })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Legs (inches)
                        </label>
                        <input
                          type="number"
                          step="0.1"
                          min="0"
                          value={metricsForm.legs_inches || ''}
                          onChange={(e) => setMetricsForm({ ...metricsForm, legs_inches: parseFloat(e.target.value) })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                        />
                      </div>
                      <div className="md:col-span-2">
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Measurement Date
                        </label>
                        <input
                          type="date"
                          value={metricsForm.measurement_date || format(new Date(), 'yyyy-MM-dd')}
                          onChange={(e) => setMetricsForm({ ...metricsForm, measurement_date: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                        />
                      </div>
                      <div className="md:col-span-2">
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Notes
                        </label>
                        <textarea
                          value={metricsForm.notes || ''}
                          onChange={(e) => setMetricsForm({ ...metricsForm, notes: e.target.value })}
                          rows={3}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                        />
                      </div>
                    </div>
                    <div className="flex gap-3">
                      <button
                        type="submit"
                        disabled={logMetricsMutation.isPending}
                        className="flex items-center gap-2 px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors"
                      >
                        <Save className="w-5 h-5" />
                        {logMetricsMutation.isPending ? 'Logging...' : 'Log Metrics'}
                      </button>
                      <button
                        type="button"
                        onClick={() => setShowMetricsForm(false)}
                        className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                      >
                        Cancel
                      </button>
                    </div>
                  </form>
                </div>
              )}

              {/* Metrics History */}
              <div>
                <h3 className="text-lg font-semibold mb-4">Metrics History</h3>
                {metricsHistory && metricsHistory.length > 0 ? (
                  <div className="space-y-3">
                    {metricsHistory.map((metric) => (
                      <div
                        key={metric.id}
                        className="bg-gray-50 rounded-lg p-4 border border-gray-200"
                      >
                        <div className="flex justify-between items-start">
                          <div>
                            <div className="font-semibold">
                              {format(parseISO(metric.date), 'MMM d, yyyy')}
                            </div>
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-2 text-sm">
                              <div>
                                <span className="text-gray-500">Weight:</span>{' '}
                                <span className="font-medium">{metric.weight_lbs.toFixed(1)} lbs</span>
                              </div>
                              {metric.body_fat_pct && (
                                <div>
                                  <span className="text-gray-500">Body Fat:</span>{' '}
                                  <span className="font-medium">{metric.body_fat_pct.toFixed(1)}%</span>
                                </div>
                              )}
                              {metric.muscle_mass_lbs && (
                                <div>
                                  <span className="text-gray-500">Muscle:</span>{' '}
                                  <span className="font-medium">{metric.muscle_mass_lbs.toFixed(1)} lbs</span>
                                </div>
                              )}
                              {(metric.waist_inches || metric.chest_inches) && (
                                <div>
                                  <span className="text-gray-500">Measurements:</span>{' '}
                                  <span className="font-medium">
                                    {metric.waist_inches && `W:${metric.waist_inches.toFixed(1)}`}
                                    {metric.chest_inches && ` C:${metric.chest_inches.toFixed(1)}`}
                                  </span>
                                </div>
                              )}
                            </div>
                            {metric.notes && (
                              <div className="mt-2 text-sm text-gray-600 italic">{metric.notes}</div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="bg-gray-50 rounded-lg p-8 text-center text-gray-500">
                    No body metrics logged yet. Click "Log Metrics" to get started.
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Preferences Tab */}
          {activeTab === 'preferences' && (
            <div className="space-y-6">
              <h2 className="text-xl font-semibold">Preferences</h2>
              <form onSubmit={handleProfileSubmit} className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Dietary Restrictions
                  </label>
                  <input
                    type="text"
                    placeholder="e.g., vegetarian, vegan, gluten-free (comma separated)"
                    defaultValue={user.dietary_restrictions?.join(', ') || ''}
                    onChange={(e) =>
                      setProfileForm({
                        ...profileForm,
                        dietary_restrictions: e.target.value.split(',').map((s) => s.trim()).filter(Boolean),
                      })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Food Dislikes
                  </label>
                  <input
                    type="text"
                    placeholder="e.g., mushrooms, olives, spicy food (comma separated)"
                    defaultValue={user.food_dislikes?.join(', ') || ''}
                    onChange={(e) =>
                      setProfileForm({
                        ...profileForm,
                        food_dislikes: e.target.value.split(',').map((s) => s.trim()).filter(Boolean),
                      })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Available Equipment
                  </label>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    {COMMON_EQUIPMENT.map((equipment) => (
                      <label key={equipment} className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          defaultChecked={user.available_equipment?.includes(equipment)}
                          onChange={(e) => {
                            const current = profileForm.available_equipment || user.available_equipment || [];
                            const updated = e.target.checked
                              ? [...current, equipment]
                              : current.filter((eq) => eq !== equipment);
                            setProfileForm({ ...profileForm, available_equipment: updated });
                          }}
                          className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                        />
                        <span className="text-sm">
                          {equipment.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                        </span>
                      </label>
                    ))}
                  </div>
                </div>
                <div className="flex justify-end">
                  <button
                    type="submit"
                    disabled={updateUserMutation.isPending}
                    className="flex items-center gap-2 px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors"
                  >
                    <Save className="w-5 h-5" />
                    {updateUserMutation.isPending ? 'Saving...' : 'Save Preferences'}
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* Security Tab */}
          {activeTab === 'security' && (
            <div className="space-y-8">
              <h2 className="text-xl font-semibold">Security Settings</h2>

              {/* Change Password Section */}
              <div className="border border-gray-200 rounded-lg p-6">
                <div className="flex items-center gap-3 mb-4">
                  <Lock className="w-6 h-6 text-primary-600" />
                  <h3 className="text-lg font-semibold">Change Password</h3>
                </div>
                <p className="text-sm text-gray-600 mb-6">
                  Update your password to keep your account secure. Use a strong password with at least 8 characters.
                </p>
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    if (passwordForm.newPassword !== passwordForm.confirmPassword) {
                      showError('New password and confirmation do not match');
                      return;
                    }
                    if (passwordForm.newPassword.length < 8) {
                      showError('Password must be at least 8 characters long');
                      return;
                    }
                    changePasswordMutation.mutate();
                  }}
                  className="space-y-4"
                >
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Current Password
                    </label>
                    <input
                      type="password"
                      required
                      value={passwordForm.currentPassword}
                      onChange={(e) =>
                        setPasswordForm({ ...passwordForm, currentPassword: e.target.value })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      placeholder="Enter your current password"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      New Password
                    </label>
                    <input
                      type="password"
                      required
                      minLength={8}
                      value={passwordForm.newPassword}
                      onChange={(e) =>
                        setPasswordForm({ ...passwordForm, newPassword: e.target.value })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      placeholder="Enter your new password (min. 8 characters)"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Confirm New Password
                    </label>
                    <input
                      type="password"
                      required
                      minLength={8}
                      value={passwordForm.confirmPassword}
                      onChange={(e) =>
                        setPasswordForm({ ...passwordForm, confirmPassword: e.target.value })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      placeholder="Confirm your new password"
                    />
                  </div>
                  <div className="flex justify-end">
                    <button
                      type="submit"
                      disabled={changePasswordMutation.isPending}
                      className="flex items-center gap-2 px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors"
                    >
                      <Lock className="w-5 h-5" />
                      {changePasswordMutation.isPending ? 'Changing...' : 'Change Password'}
                    </button>
                  </div>
                </form>
              </div>

              {/* Change Email Section */}
              <div className="border border-gray-200 rounded-lg p-6">
                <div className="flex items-center gap-3 mb-4">
                  <Mail className="w-6 h-6 text-primary-600" />
                  <h3 className="text-lg font-semibold">Change Email Address</h3>
                </div>
                <p className="text-sm text-gray-600 mb-6">
                  Update your email address. You'll need to enter your current password to confirm the change.
                </p>
                {user.email && (
                  <div className="mb-4 p-3 bg-gray-50 rounded-lg">
                    <span className="text-sm text-gray-600">Current email: </span>
                    <span className="text-sm font-medium text-gray-900">{user.email}</span>
                  </div>
                )}
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    if (!emailForm.newEmail.includes('@')) {
                      showError('Please enter a valid email address');
                      return;
                    }
                    changeEmailMutation.mutate();
                  }}
                  className="space-y-4"
                >
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      New Email Address
                    </label>
                    <input
                      type="email"
                      required
                      value={emailForm.newEmail}
                      onChange={(e) =>
                        setEmailForm({ ...emailForm, newEmail: e.target.value })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      placeholder="Enter your new email address"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Current Password
                    </label>
                    <input
                      type="password"
                      required
                      value={emailForm.password}
                      onChange={(e) =>
                        setEmailForm({ ...emailForm, password: e.target.value })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      placeholder="Enter your current password to confirm"
                    />
                  </div>
                  <div className="flex justify-end">
                    <button
                      type="submit"
                      disabled={changeEmailMutation.isPending}
                      className="flex items-center gap-2 px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors"
                    >
                      <Mail className="w-5 h-5" />
                      {changeEmailMutation.isPending ? 'Changing...' : 'Change Email'}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
