import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Avatar,
  Chip,
  TextField,
  InputAdornment,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Snackbar,
  CircularProgress,
  Tooltip,
  TablePagination,
  Checkbox,
  Menu,
  MenuItem as MenuItemComponent,
} from '@mui/material';
import {
  Add,
  Search,
  Edit,
  Delete,
  MoreVert,
  FilterList,
  Person,
  Email,
  Phone,
  Refresh,
  Download,
  Upload,
  Block,
  CheckCircle,
  School,
  Work,
  AdminPanelSettings,
  Notifications,
  Send,
} from '@mui/icons-material';
import { userApiService } from '../../services/userApi';
import { useAuth } from '../../contexts/AuthContext';
// Utility function for date formatting
const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
};

const UserManagement = () => {
  const { user: currentUser } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [selectedUsers, setSelectedUsers] = useState([]);
  const [editDialog, setEditDialog] = useState({ open: false, user: null, mode: 'create' });
  const [deleteDialog, setDeleteDialog] = useState({ open: false, user: null });
  const [bulkDialog, setBulkDialog] = useState({ open: false, action: '' });
  const [notificationDialog, setNotificationDialog] = useState({ open: false });
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [anchorEl, setAnchorEl] = useState(null);
  const [contextMenuUser, setContextMenuUser] = useState(null);

  const [editFormData, setEditFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    username: '',
    role: 'student',
    phone_number: '',
    date_of_birth: '',
    is_active: true,
  });

  const [notificationForm, setNotificationForm] = useState({
    title: '',
    message: '',
    recipient_type: 'all',
    priority: 'normal'
  });

  useEffect(() => {
    fetchUsers();
  }, [searchTerm, roleFilter, page, rowsPerPage]);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const params = {
        search: searchTerm,
        role: roleFilter,
        page: page + 1,
        page_size: rowsPerPage,
      };
      const response = await userApiService.getUsers(params);
      setUsers(response.results || response);
    } catch (error) {
      console.error('Error fetching users:', error);
      showSnackbar('Failed to fetch users', 'error');
    } finally {
      setLoading(false);
    }
  };

  const showSnackbar = (message, severity = 'success') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleContextMenu = (event, user) => {
    event.preventDefault();
    setAnchorEl(event.currentTarget);
    setContextMenuUser(user);
  };

  const closeContextMenu = () => {
    setAnchorEl(null);
    setContextMenuUser(null);
  };

  const openEditDialog = (user = null, mode = 'create') => {
    if (user) {
      setEditFormData({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        email: user.email || '',
        username: user.username || '',
        role: user.role || 'student',
        phone_number: user.phone_number || '',
        date_of_birth: user.date_of_birth || '',
        is_active: user.is_active !== undefined ? user.is_active : true,
      });
    } else {
      setEditFormData({
        first_name: '',
        last_name: '',
        email: '',
        username: '',
        role: 'student',
        phone_number: '',
        date_of_birth: '',
        is_active: true,
      });
    }
    setEditDialog({ open: true, user, mode });
    closeContextMenu();
  };

  const closeEditDialog = () => {
    setEditDialog({ open: false, user: null, mode: 'create' });
    setEditFormData({
      first_name: '',
      last_name: '',
      email: '',
      username: '',
      role: 'student',
      phone_number: '',
      date_of_birth: '',
      is_active: true,
    });
  };

  const handleSaveUser = async () => {
    try {
      if (editDialog.mode === 'create') {
        await userApiService.createUser(editFormData);
        showSnackbar('User created successfully');
      } else {
        await userApiService.updateUser(editDialog.user.id, editFormData);
        showSnackbar('User updated successfully');
      }
      closeEditDialog();
      fetchUsers();
    } catch (error) {
      console.error('Error saving user:', error);
      showSnackbar('Failed to save user', 'error');
    }
  };

  const handleDeleteUser = async () => {
    try {
      await userApiService.deleteUser(deleteDialog.user.id);
      setDeleteDialog({ open: false, user: null });
      showSnackbar('User deactivated successfully');
      fetchUsers();
    } catch (error) {
      console.error('Error deleting user:', error);
      showSnackbar('Failed to delete user', 'error');
    }
  };

  const handleBulkAction = async () => {
    try {
      if (bulkDialog.action === 'delete') {
        await userApiService.bulkDeleteUsers(selectedUsers);
        showSnackbar(`${selectedUsers.length} users deactivated`);
      } else if (bulkDialog.action === 'activate') {
        await userApiService.bulkUpdateUsers(selectedUsers, { is_active: true });
        showSnackbar(`${selectedUsers.length} users activated`);
      } else if (bulkDialog.action === 'deactivate') {
        await userApiService.bulkUpdateUsers(selectedUsers, { is_active: false });
        showSnackbar(`${selectedUsers.length} users deactivated`);
      }
      setBulkDialog({ open: false, action: '' });
      setSelectedUsers([]);
      fetchUsers();
    } catch (error) {
      console.error('Error performing bulk action:', error);
      showSnackbar('Failed to perform bulk action', 'error');
    }
  };

  const handleSendNotification = async () => {
    try {
      const notificationData = {
        title: notificationForm.title,
        message: notificationForm.message,
        recipient_type: notificationForm.recipient_type,
        priority: notificationForm.priority
      };

      const response = await userApiService.sendNotificationToStudents(notificationData);
      setNotificationDialog({ open: false });
      setNotificationForm({
        title: '',
        message: '',
        recipient_type: 'all',
        priority: 'normal'
      });
      showSnackbar(response.message || 'Notification sent successfully');
    } catch (error) {
      console.error('Error sending notification:', error);
      showSnackbar('Failed to send notification', 'error');
    }
  };

  const handleSelectAll = (event) => {
    if (event.target.checked) {
      setSelectedUsers(users.map(user => user.id));
    } else {
      setSelectedUsers([]);
    }
  };

  const handleSelectUser = (userId) => {
    setSelectedUsers(prev => 
      prev.includes(userId) 
        ? prev.filter(id => id !== userId)
        : [...prev, userId]
    );
  };

  const getRoleIcon = (role) => {
    switch (role) {
      case 'admin': return <AdminPanelSettings />;
      case 'teacher': return <Work />;
      case 'student': return <School />;
      default: return <Person />;
    }
  };

  const getRoleColor = (role) => {
    switch (role) {
      case 'admin': return 'error';
      case 'teacher': return 'success';
      case 'student': return 'primary';
      default: return 'default';
    }
  };

  const filteredUsers = users.filter(user => 
    user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
    `${user.first_name} ${user.last_name}`.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" fontWeight="bold">
          See Users
        </Typography>
        <Box display="flex" gap={2}>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={fetchUsers}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<Send />}
            onClick={() => setNotificationDialog({ open: true })}
          >
            Send Notification
          </Button>
        </Box>
      </Box>

      {/* Filters and Search */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={6} md={4}>
              <TextField
                fullWidth
                placeholder="Search users..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Search />
                    </InputAdornment>
                  ),
                }}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth>
                <InputLabel>Role Filter</InputLabel>
                <Select
                  value={roleFilter}
                  label="Role Filter"
                  onChange={(e) => setRoleFilter(e.target.value)}
                >
                  <MenuItem value="">All Roles</MenuItem>
                  <MenuItem value="student">Students</MenuItem>
                  <MenuItem value="teacher">Teachers</MenuItem>
                  <MenuItem value="admin">Admins</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            {selectedUsers.length > 0 && (
              <Grid item xs={12} sm={12} md={5}>
                <Box display="flex" gap={1} alignItems="center">
                  <Typography variant="body2" color="text.secondary">
                    {selectedUsers.length} selected
                  </Typography>
                  <Button
                    size="small"
                    onClick={() => setBulkDialog({ open: true, action: 'activate' })}
                  >
                    Activate
                  </Button>
                  <Button
                    size="small"
                    onClick={() => setBulkDialog({ open: true, action: 'deactivate' })}
                  >
                    Deactivate
                  </Button>
                  <Button
                    size="small"
                    color="error"
                    onClick={() => setBulkDialog({ open: true, action: 'delete' })}
                  >
                    Delete
                  </Button>
                </Box>
              </Grid>
            )}
          </Grid>
        </CardContent>
      </Card>

      {/* Users Table */}
      <Card>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell padding="checkbox">
                  <Checkbox
                    indeterminate={selectedUsers.length > 0 && selectedUsers.length < users.length}
                    checked={users.length > 0 && selectedUsers.length === users.length}
                    onChange={handleSelectAll}
                  />
                </TableCell>
                <TableCell>User</TableCell>
                <TableCell>Role</TableCell>
                <TableCell>Contact</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Joined</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={7} align="center" sx={{ py: 3 }}>
                    <CircularProgress />
                  </TableCell>
                </TableRow>
              ) : filteredUsers.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} align="center" sx={{ py: 3 }}>
                    <Typography color="text.secondary">
                      No users found
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                filteredUsers
                  .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                  .map((user) => (
                    <TableRow
                      key={user.id}
                      hover
                      onContextMenu={(e) => handleContextMenu(e, user)}
                    >
                      <TableCell padding="checkbox">
                        <Checkbox
                          checked={selectedUsers.includes(user.id)}
                          onChange={() => handleSelectUser(user.id)}
                        />
                      </TableCell>
                      <TableCell>
                        <Box display="flex" alignItems="center" gap={2}>
                          <Avatar
                            src={user.profile_picture}
                            alt={user.first_name || user.username}
                            sx={{ width: 40, height: 40 }}
                          >
                            {user.first_name?.[0] || user.username?.[0] || 'U'}
                          </Avatar>
                          <Box>
                            <Typography variant="body1" fontWeight="medium">
                              {user.first_name && user.last_name
                                ? `${user.first_name} ${user.last_name}`
                                : user.username}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              {user.email}
                            </Typography>
                          </Box>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip
                          icon={getRoleIcon(user.role)}
                          label={user.role?.toUpperCase()}
                          color={getRoleColor(user.role)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Box>
                          <Typography variant="body2" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                            <Email fontSize="small" />
                            {user.email}
                          </Typography>
                          {user.phone_number && (
                            <Typography variant="body2" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 0.5 }}>
                              <Phone fontSize="small" />
                              {user.phone_number}
                            </Typography>
                          )}
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box display="flex" alignItems="center" gap={1}>
                          <Chip
                            label={user.is_active ? 'Active' : 'Inactive'}
                            color={user.is_active ? 'success' : 'default'}
                            size="small"
                          />
                          {user.is_verified && (
                            <CheckCircle color="success" fontSize="small" />
                          )}
                        </Box>
                      </TableCell>
                      <TableCell>
                        {user.created_at && formatDate(user.created_at)}
                      </TableCell>
                      <TableCell align="right">
                        <IconButton
                          onClick={() => openEditDialog(user, 'edit')}
                          size="small"
                        >
                          <Edit />
                        </IconButton>
                        <IconButton
                          onClick={() => setDeleteDialog({ open: true, user })}
                          size="small"
                          color="error"
                        >
                          <Delete />
                        </IconButton>
                        <IconButton
                          onClick={(e) => handleContextMenu(e, user)}
                          size="small"
                        >
                          <MoreVert />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
        
        <TablePagination
          component="div"
          count={filteredUsers.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={(_, newPage) => setPage(newPage)}
          onRowsPerPageChange={(e) => {
            setRowsPerPage(parseInt(e.target.value, 10));
            setPage(0);
          }}
        />
      </Card>

      {/* Context Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={closeContextMenu}
      >
        <MenuItemComponent onClick={() => openEditDialog(contextMenuUser, 'edit')}>
          <Edit fontSize="small" sx={{ mr: 1 }} />
          Edit User
        </MenuItemComponent>
        <MenuItemComponent onClick={() => setDeleteDialog({ open: true, user: contextMenuUser })}>
          <Delete fontSize="small" sx={{ mr: 1 }} />
          Delete User
        </MenuItemComponent>
        <MenuItemComponent onClick={closeContextMenu}>
          <Block fontSize="small" sx={{ mr: 1 }} />
          {contextMenuUser?.is_active ? 'Deactivate' : 'Activate'}
        </MenuItemComponent>
      </Menu>

      {/* Edit/Create User Dialog */}
      <Dialog open={editDialog.open} onClose={closeEditDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editDialog.mode === 'create' ? 'Add New User' : 'Edit User'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="First Name"
                value={editFormData.first_name}
                onChange={(e) => setEditFormData({ ...editFormData, first_name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Last Name"
                value={editFormData.last_name}
                onChange={(e) => setEditFormData({ ...editFormData, last_name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Email"
                type="email"
                value={editFormData.email}
                onChange={(e) => setEditFormData({ ...editFormData, email: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Username"
                value={editFormData.username}
                onChange={(e) => setEditFormData({ ...editFormData, username: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Role</InputLabel>
                <Select
                  value={editFormData.role}
                  label="Role"
                  onChange={(e) => setEditFormData({ ...editFormData, role: e.target.value })}
                >
                  <MenuItem value="student">Student</MenuItem>
                  <MenuItem value="teacher">Teacher</MenuItem>
                  {currentUser?.role === 'admin' && (
                    <MenuItem value="admin">Admin</MenuItem>
                  )}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Phone Number"
                value={editFormData.phone_number}
                onChange={(e) => setEditFormData({ ...editFormData, phone_number: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Date of Birth"
                type="date"
                value={editFormData.date_of_birth}
                onChange={(e) => setEditFormData({ ...editFormData, date_of_birth: e.target.value })}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={closeEditDialog}>Cancel</Button>
          <Button onClick={handleSaveUser} variant="contained">
            {editDialog.mode === 'create' ? 'Create User' : 'Update User'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialog.open} onClose={() => setDeleteDialog({ open: false, user: null })}>
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to deactivate the user "{deleteDialog.user?.username}"?
            This action will set the user as inactive but preserve all their data.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialog({ open: false, user: null })}>
            Cancel
          </Button>
          <Button onClick={handleDeleteUser} color="error" variant="contained">
            Deactivate User
          </Button>
        </DialogActions>
      </Dialog>

      {/* Bulk Action Confirmation Dialog */}
      <Dialog open={bulkDialog.open} onClose={() => setBulkDialog({ open: false, action: '' })}>
        <DialogTitle>Confirm Bulk Action</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to {bulkDialog.action} {selectedUsers.length} selected user(s)?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setBulkDialog({ open: false, action: '' })}>
            Cancel
          </Button>
          <Button onClick={handleBulkAction} color="primary" variant="contained">
            Confirm
          </Button>
        </DialogActions>
      </Dialog>

      {/* Send Notification Dialog */}
      <Dialog 
        open={notificationDialog.open} 
        onClose={() => setNotificationDialog({ open: false })}
        maxWidth="md" 
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center" gap={1}>
            <Send />
            Send Notification to Students
          </Box>
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Notification Title"
                value={notificationForm.title}
                onChange={(e) => setNotificationForm({ ...notificationForm, title: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Message"
                multiline
                rows={4}
                value={notificationForm.message}
                onChange={(e) => setNotificationForm({ ...notificationForm, message: e.target.value })}
                required
                placeholder="Enter your message to students..."
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Recipients</InputLabel>
                <Select
                  value={notificationForm.recipient_type}
                  label="Recipients"
                  onChange={(e) => setNotificationForm({ ...notificationForm, recipient_type: e.target.value })}
                >
                  <MenuItem value="all">All Students</MenuItem>
                  <MenuItem value="active_only">Active Students Only</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Priority</InputLabel>
                <Select
                  value={notificationForm.priority}
                  label="Priority"
                  onChange={(e) => setNotificationForm({ ...notificationForm, priority: e.target.value })}
                >
                  <MenuItem value="low">Low</MenuItem>
                  <MenuItem value="normal">Normal</MenuItem>
                  <MenuItem value="high">High</MenuItem>
                  <MenuItem value="urgent">Urgent</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setNotificationDialog({ open: false })}>
            Cancel
          </Button>
          <Button 
            onClick={handleSendNotification} 
            variant="contained" 
            startIcon={<Send />}
            disabled={!notificationForm.title || !notificationForm.message}
          >
            Send Notification
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        message={snackbar.message}
      />
    </Box>
  );
};

export default UserManagement;
