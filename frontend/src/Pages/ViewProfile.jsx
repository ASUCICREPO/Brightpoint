import React from 'react';
import { Box, Typography, Divider, Chip } from '@mui/material';
import { useLocation, useNavigate } from 'react-router-dom';
import AppHeader from '../Components/AppHeader';
import { useUser } from '../utilities/UserContext';

const UserProfile = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const isAdmin = location.pathname.startsWith('/admin');

  const { userData } = useUser();

  // ✅ Helper function to get the username display value (username or user_id)
  const getDisplayUsername = () => {
    const username = userData?.username?.toString().trim();
    const user_id = userData?.user_id?.toString().trim();

    // Return username if it exists and is not empty, otherwise return user_id
    return username || user_id || "-";
  };

  // ✅ Helper function to get full name
  const getFullName = () => {
    const firstName = userData?.firstName?.toString().trim() || '';
    const lastName = userData?.lastName?.toString().trim() || '';

    if (firstName && lastName) {
      return `${firstName} ${lastName}`;
    } else if (firstName) {
      return firstName;
    } else if (lastName) {
      return lastName;
    }
    return "-";
  };

  // ✅ Helper function to get phone number with all possible field variations
  const getPhoneNumber = () => {
    // Try all possible phone number field names
    const phoneFields = [
      userData?.phoneNumber,      // camelCase (most common in React)
      userData?.Phone,           // API format (capital P)
      userData?.phone,           // lowercase
      userData?.phonenumber,     // form field name
      userData?.phoneNum,        // another variation
      userData?.mobile,          // alternative field name
    ];

    // Return the first non-empty value
    const phoneNumber = phoneFields.find(field =>
      field && field.toString().trim() !== ''
    );

    return phoneNumber?.toString().trim() || "-";
  };

  // ✅ Helper function to get zipcode with variations
  const getZipcode = () => {
    return userData?.zipcode ||
           userData?.Zipcode ||
           userData?.zip ||
           userData?.postalCode ||
           "-";
  };

  // ✅ FIXED: Helper function to format dates without timezone issues
  const formatDateFromString = (dateString) => {
    if (!dateString) return "-";

    // Parse the date string manually to avoid timezone issues
    const [year, month, day] = dateString.split('-').map(Number);
    const date = new Date(year, month - 1, day); // month is 0-indexed

    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  // ✅ NEW: Helper function to format children birth dates
  const getChildrenInfo = () => {
    const children = userData?.children_birth_dates || [];

    if (!children || children.length === 0) {
      return "-";
    }

    return children.map((birthDate, index) => {
      const formattedDate = formatDateFromString(birthDate);
      return `Child ${index + 1}: ${formattedDate}`;
    }).join(', ');
  };

  // ✅ NEW: Helper function to format expected due date
  const getExpectedDueDate = () => {
    const dueDate = userData?.expected_due_date;
    return formatDateFromString(dueDate);
  };

  // ✅ FIXED: Helper function to calculate child ages without timezone issues
  const getChildAges = () => {
    const children = userData?.children_birth_dates || [];

    if (!children || children.length === 0) {
      return [];
    }

    return children.map((birthDate, index) => {
      // Parse date manually to avoid timezone issues
      const [year, month, day] = birthDate.split('-').map(Number);
      const birth = new Date(year, month - 1, day);
      const today = new Date();

      let age = today.getFullYear() - birth.getFullYear();
      const monthDiff = today.getMonth() - birth.getMonth();

      if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
        age--;
      }

      return {
        childNumber: index + 1,
        age: age,
        birthDate: birthDate
      };
    });
  };

  const renderField = (label, value) => (
    <Box mb={2}>
      <Typography variant="body2" color="textSecondary">{label}:</Typography>
      <Typography variant="body1">
        {value?.toString().trim() ? value : "-"}
      </Typography>
    </Box>
  );

  // ✅ NEW: Render children with ages as chips
  const renderChildrenField = (label) => {
    const childAges = getChildAges();

    return (
      <Box mb={2}>
        <Typography variant="body2" color="textSecondary">{label}:</Typography>
        {childAges.length > 0 ? (
          <Box display="flex" flexWrap="wrap" gap={1} mt={1}>
            {childAges.map((child) => (
              <Chip
                key={child.childNumber}
                label={`Child ${child.childNumber}: ${child.age} years old`}
                variant="outlined"
                size="small"
                sx={{
                  backgroundColor: '#f5f5f5',
                  color: '#1F1463',
                  borderColor: '#1F1463'
                }}
              />
            ))}
          </Box>
        ) : (
          <Typography variant="body1" color="textSecondary">
            No children information available
          </Typography>
        )}
      </Box>
    );
  };

  const handleBack = () => {
    navigate(-1);
  };

  // ✅ Debug: Log userData to see what's available
  console.log("UserProfile - Current userData:", userData);
  console.log("Children birth dates:", userData?.children_birth_dates);
  console.log("Expected due date:", userData?.expected_due_date);

  return (
    <Box bgcolor="white" minHeight="100vh">
      <AppHeader
        username={getDisplayUsername()}
        showSwitch={true}
        style={{ position: 'sticky', top: 0, zIndex: 999 }}
      />

      <Box display="flex" justifyContent="center" alignItems="center" mt={4} px={2}>
        <Typography
          variant="body2"
          sx={{ color: '#1F1463', cursor: 'pointer' }}
          onClick={handleBack}
        >
          &lt; Back to chat
        </Typography>
      </Box>

      <Box display="flex" justifyContent="center" alignItems="center" mt={4} px={2}>
        <Box
          width="100%"
          maxWidth="600px"
          bgcolor="white"
          p={4}
          borderRadius={4}
          boxShadow={3}
        >
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
            <Typography variant="h5" fontWeight="bold" color="#1F1463">
              {isAdmin ? "Admin Profile" : "User Profile"}
            </Typography>
          </Box>

          <Box display="grid" gridTemplateColumns="1fr 1fr" gap={2}>
            {isAdmin ? (
              <>
                {renderField("Name", "Admin")}
                {renderField("Email", "admin@gmail.com")}
              </>
            ) : (
              <>
                {renderField("Username", getDisplayUsername())}
                {renderField("Full Name", getFullName())}
                {renderField("Email", userData?.email)}
                {renderField("ZipCode", getZipcode())}
                {renderField("Phone Number", getPhoneNumber())}
                {renderField("Language", userData?.language || "english")}
              </>
            )}
          </Box>

          {!isAdmin && (
            <>
              <Divider sx={{ my: 4 }} />
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h5" fontWeight="bold" color="#1F1463">
                  Family Information
                </Typography>
              </Box>

              {/* ✅ NEW: Enhanced children section */}
              <Box display="flex" flexDirection="column" gap={2}>
                {renderChildrenField("Children")}

                {/* ✅ Show detailed birth dates with fixed formatting */}
                {userData?.children_birth_dates && userData.children_birth_dates.length > 0 && (
                  <Box mb={2}>
                    <Typography variant="body2" color="textSecondary">Children Birth Dates:</Typography>
                    <Box mt={1}>
                      {userData.children_birth_dates.map((date, index) => (
                        <Typography key={index} variant="body2" sx={{ ml: 2 }}>
                          • Child {index + 1}: {formatDateFromString(date)}
                        </Typography>
                      ))}
                    </Box>
                  </Box>
                )}

                {/* ✅ Expected due date */}
                {renderField("Expected Due Date", getExpectedDueDate())}

                {/* ✅ Legacy support for existing childInfo field */}
                {userData?.childInfo && renderField("Additional Child Info", userData.childInfo)}
                {userData?.dueDate && renderField("Legacy Due Date", userData.dueDate)}
              </Box>

              {/* ✅ Debug section (remove in production) */}
              {process.env.NODE_ENV === 'development' && (
                <>
                  <Divider sx={{ my: 2 }} />
                  <Box bgcolor="#f5f5f5" p={2} borderRadius={2}>
                    <Typography variant="caption" color="textSecondary">
                      Debug Info (Dev Only):
                    </Typography>
                    <Typography variant="caption" display="block">
                      Children count: {userData?.children_birth_dates?.length || 0}
                    </Typography>
                    <Typography variant="caption" display="block">
                      Has due date: {userData?.expected_due_date ? 'Yes' : 'No'}
                    </Typography>
                    <Typography variant="caption" display="block">
                      First name: {userData?.firstName || 'Not set'}
                    </Typography>
                    <Typography variant="caption" display="block">
                      Last name: {userData?.lastName || 'Not set'}
                    </Typography>
                  </Box>
                </>
              )}
            </>
          )}
        </Box>
      </Box>
    </Box>
  );
};

export default UserProfile;