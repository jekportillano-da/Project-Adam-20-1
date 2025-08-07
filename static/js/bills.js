document.addEventListener('DOMContentLoaded', () => {
    // Category icons as SVG paths
    const categoryIcons = {
        housing: '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>',
        utilities: '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8h1a4 4 0 0 1 0 8h-1"></path><path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z"></path><line x1="6" y1="1" x2="6" y2="4"></line><line x1="10" y1="1" x2="10" y2="4"></line><line x1="14" y1="1" x2="14" y2="4"></line></svg>',
        transportation: '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="3" width="15" height="13"></rect><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"></polygon><circle cx="5.5" cy="18.5" r="2.5"></circle><circle cx="18.5" cy="18.5" r="2.5"></circle></svg>',
        entertainment: '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="15" rx="2" ry="2"></rect><polyline points="17 2 12 7 7 2"></polyline></svg>',
        insurance: '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>',
        subscriptions: '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg>',
        other: '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>'
    };
    
    // Check if Chart.js is available
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded. Please check your network connection or script inclusion.');
        // Show error message to user
        const chartContainer = document.querySelector('.chart-container');
        if (chartContainer) {
            chartContainer.innerHTML = `
                <div class="chart-error">
                    <p>Chart visualization could not be loaded.</p>
                    <p>Please check your internet connection and refresh the page.</p>
                </div>
            `;
        }
    }
    
    // Elements
    const billForm = document.getElementById('bill-form');
    const billNameInput = document.getElementById('bill-name');
    const billAmountInput = document.getElementById('bill-amount');
    const billCategorySelect = document.getElementById('bill-category');
    const billDueDateInput = document.getElementById('bill-due-date');
    const billsList = document.getElementById('billsList');
    const emptyMessage = document.querySelector('.empty-message');
    const totalAmount = document.querySelector('.total-amount');
    const timelineMarkers = document.getElementById('timelineMarkers');
    
    // Store for bills data
    let bills = [];
    
    // Load bills from localStorage if available
    if (localStorage.getItem('bills')) {
        try {
            bills = JSON.parse(localStorage.getItem('bills'));
            updateBillsList();
            updateTotalAmount();
            updateTimeline();
            
            // Slight delay for chart initialization to ensure DOM is ready
            setTimeout(() => {
                updateChart();
            }, 100);
        } catch (e) {
            console.error('Error loading bills from localStorage:', e);
        }
    } else {
        // If no bills, still call updateChart to show empty state
        setTimeout(() => {
            updateChart();
        }, 100);
    }
    
    // Format currency with commas and decimals
    function formatCurrency(amount) {
        return new Intl.NumberFormat('en-PH', {
            style: 'currency',
            currency: 'PHP',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(amount);
    }
    
    // Form validation and formatting
    billAmountInput.addEventListener('input', (e) => {
        let value = e.target.value.replace(/[^0-9.]/g, '');
        
        if (value) {
            const num = parseFloat(value);
            if (num <= 0) {
                e.target.setCustomValidity('Please enter a positive amount');
            } else if (num > 1000000) {
                e.target.setCustomValidity('Amount cannot exceed 1,000,000');
            } else {
                e.target.setCustomValidity('');
            }

            // Format the number with commas while typing
            const parts = value.split('.');
            parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',');
            e.target.value = parts.join('.');
        }
    });
    
    // Due date validation
    billDueDateInput.addEventListener('input', (e) => {
        const value = parseInt(e.target.value);
        if (isNaN(value) || value < 1 || value > 31) {
            e.target.setCustomValidity('Please enter a valid day (1-31)');
        } else {
            e.target.setCustomValidity('');
        }
    });
    
    // Handle form submission
    billForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        try {
            // Get and validate the form values
            const name = billNameInput.value.trim();
            if (!name) {
                return;
            }
            
            // Parse amount properly - remove commas and other non-numeric characters except decimal point
            const amountStr = billAmountInput.value.replace(/[^0-9.]/g, '');
            const amount = parseFloat(amountStr);
            if (isNaN(amount) || amount <= 0) {
                return;
            }
            
            const category = billCategorySelect.value;
            const dueDate = billDueDateInput.value ? parseInt(billDueDateInput.value) : null;
            
            // Proceed with valid form data
            
            // Create new bill object with validated data
            const newBill = {
                id: Date.now(), // Unique ID for each bill
                name,
                amount,
                category,
                dueDate
            };
            
            // Add to bills array
            bills.push(newBill);
            
            // Update storage first to ensure data is saved
            saveBills();
            
            // Then update all UI components
            updateBillsList();
            updateTotalAmount();
            updateTimeline();
            updateChart();
            
            // Show confirmation message
            showConfirmation('Bill added successfully!');
            
            // Reset form and focus on name input - use setTimeout to ensure the form is reset properly first
            billForm.reset();
            
            // Use setTimeout to ensure focus happens after browser's form reset
            setTimeout(() => {
                billNameInput.focus();
            }, 10);
        } catch (error) {
            console.error('Error adding bill:', error);
            showConfirmation('Error adding bill. Please try again.');
        }
    });
    
    // Show temporary confirmation message
    function showConfirmation(message) {
        // Create toast element if it doesn't exist
        let toast = document.getElementById('toast-notification');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'toast-notification';
            toast.className = 'toast-notification';
            document.body.appendChild(toast);
        }
        
        // Set message and show toast
        toast.textContent = message;
        toast.classList.add('show');
        
        // Hide toast after 3 seconds
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }
    
    // Handle delete button clicks
    function setupDeleteButtons() {
        document.querySelectorAll('.bill-delete').forEach(button => {
            button.addEventListener('click', (e) => {
                const id = parseInt(e.target.closest('.bill-item').dataset.id);
                bills = bills.filter(bill => bill.id !== id);
                saveBills();
                updateBillsList();
                updateTotalAmount();
                updateTimeline();
                
                // Add a slight delay before updating the chart
                setTimeout(() => {
                    updateChart();
                }, 50);
            });
        });
    }
    
    // Save bills to localStorage
    function saveBills() {
        localStorage.setItem('bills', JSON.stringify(bills));
    }
    
    // Update the bills list in the UI
    function updateBillsList() {
        if (bills.length === 0) {
            billsList.innerHTML = '';
            emptyMessage.style.display = 'block';
            return;
        }
        
        emptyMessage.style.display = 'none';
        
        // Sort bills by due date
        const sortedBills = [...bills].sort((a, b) => {
            if (a.dueDate === null) return 1;
            if (b.dueDate === null) return -1;
            return a.dueDate - b.dueDate;
        });
        
        // Generate HTML for each bill
        const billsHTML = sortedBills.map(bill => `
            <li class="bill-item" data-id="${bill.id}">
                <div class="bill-details">
                    <div class="bill-name">${bill.name}</div>
                    <div class="bill-category">${getCategoryName(bill.category)}</div>
                    ${bill.dueDate ? `<div class="bill-due">Due: Day ${bill.dueDate}</div>` : ''}
                </div>
                <div class="bill-amount">${formatCurrency(bill.amount)}</div>
                <div class="bill-actions">
                    <button class="bill-delete">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M3 6h18"></path>
                            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"></path>
                            <path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                        </svg>
                    </button>
                </div>
            </li>
        `).join('');
        
        billsList.innerHTML = billsHTML;
        setupDeleteButtons();
    }
    
    // Get readable category name
    function getCategoryName(categoryKey) {
        const categories = {
            housing: 'Housing',
            utilities: 'Utilities',
            transportation: 'Transportation',
            entertainment: 'Entertainment',
            insurance: 'Insurance',
            subscriptions: 'Subscriptions',
            other: 'Other'
        };
        return categories[categoryKey] || categoryKey.charAt(0).toUpperCase() + categoryKey.slice(1);
    }
    
    // Update total amount
    function updateTotalAmount() {
        const total = bills.reduce((sum, bill) => sum + bill.amount, 0);
        totalAmount.textContent = formatCurrency(total);
    }
    
    // Update timeline
    function updateTimeline() {
        // Only show bills with due dates
        const billsWithDueDate = bills.filter(bill => bill.dueDate !== null);
        
        if (billsWithDueDate.length === 0) {
            timelineMarkers.innerHTML = '<div class="no-dates">No due dates specified</div>';
            return;
        }
        
        timelineMarkers.innerHTML = '';
        
        // Add today's marker
        const today = new Date();
        const dayOfMonth = today.getDate();
        let todayPosition;
        
        // Calculate today's position using the same logic as for bill markers
        if (dayOfMonth === 1) {
            todayPosition = 0;
        } else if (dayOfMonth === 5) {
            todayPosition = 13.33;
        } else if (dayOfMonth === 10) {
            todayPosition = 30;
        } else if (dayOfMonth === 15) {
            todayPosition = 46.67;
        } else if (dayOfMonth === 20) {
            todayPosition = 63.33;
        } else if (dayOfMonth === 25) {
            todayPosition = 80;
        } else if (dayOfMonth === 30 || dayOfMonth === 31) {
            todayPosition = 100;
        } else {
            // For days in between the marks, calculate proportionally
            if (dayOfMonth < 5) {
                todayPosition = (dayOfMonth - 1) / 4 * 13.33;
            } else if (dayOfMonth < 10) {
                todayPosition = 13.33 + (dayOfMonth - 5) / 5 * (30 - 13.33);
            } else if (dayOfMonth < 15) {
                todayPosition = 30 + (dayOfMonth - 10) / 5 * (46.67 - 30);
            } else if (dayOfMonth < 20) {
                todayPosition = 46.67 + (dayOfMonth - 15) / 5 * (63.33 - 46.67);
            } else if (dayOfMonth < 25) {
                todayPosition = 63.33 + (dayOfMonth - 20) / 5 * (80 - 63.33);
            } else {
                todayPosition = 80 + (dayOfMonth - 25) / 5 * (100 - 80);
            }
        }
        
        const todayMarker = document.createElement('div');
        todayMarker.className = 'today-marker';
        todayMarker.style.left = `${todayPosition}%`;
        timelineMarkers.appendChild(todayMarker);
        
        // Group bills by due date to handle multiple bills on the same day
        const billsByDate = billsWithDueDate.reduce((groups, bill) => {
            if (!groups[bill.dueDate]) {
                groups[bill.dueDate] = [];
            }
            groups[bill.dueDate].push(bill);
            return groups;
        }, {});
        
        // Category colors for consistency
        const categoryColors = {
            housing: '#FF9800',
            utilities: '#4CAF50',
            transportation: '#2196F3',
            entertainment: '#9C27B0',
            insurance: '#607D8B',
            subscriptions: '#E91E63',
            other: '#795548'
        };
        
        // Create markers for each bill, with special handling for date groups
        Object.entries(billsByDate).forEach(([dueDate, dateBills]) => {
            // Calculate position properly aligned with timeline day indicators
            const dayNum = parseInt(dueDate);
            
            // More precise positioning calculation to align with days
            let datePosition;
            if (dayNum === 1) {
                datePosition = 0;
            } else if (dayNum === 5) {
                datePosition = 13.33;
            } else if (dayNum === 10) {
                datePosition = 30;
            } else if (dayNum === 15) {
                datePosition = 46.67;
            } else if (dayNum === 20) {
                datePosition = 63.33;
            } else if (dayNum === 25) {
                datePosition = 80;
            } else if (dayNum === 30 || dayNum === 31) {
                datePosition = 100;
            } else {
                // For days in between the marks, calculate proportionally
                if (dayNum < 5) {
                    datePosition = (dayNum - 1) / 4 * 13.33;
                } else if (dayNum < 10) {
                    datePosition = 13.33 + (dayNum - 5) / 5 * (30 - 13.33);
                } else if (dayNum < 15) {
                    datePosition = 30 + (dayNum - 10) / 5 * (46.67 - 30);
                } else if (dayNum < 20) {
                    datePosition = 46.67 + (dayNum - 15) / 5 * (63.33 - 46.67);
                } else if (dayNum < 25) {
                    datePosition = 63.33 + (dayNum - 20) / 5 * (80 - 63.33);
                } else {
                    datePosition = 80 + (dayNum - 25) / 5 * (100 - 80);
                }
            }
            
            // If there are multiple bills on the same date, create a date group
            if (dateBills.length > 1) {
                const dateGroup = document.createElement('div');
                dateGroup.className = 'timeline-date-group';
                dateGroup.style.left = `${datePosition}%`;
                
                // Calculate how to distribute the markers vertically
                const middleIndex = (dateBills.length - 1) / 2;
                
                // Add each bill in the group with vertical offset
                dateBills.forEach((bill, index) => {
                    const marker = document.createElement('div');
                    marker.className = 'timeline-marker';
                    
                    // Calculate vertical positioning to center the group
                    // With more items, spread them out more
                    const spacingFactor = Math.min(15, 40 / dateBills.length);
                    const verticalOffset = (index - middleIndex) * spacingFactor;
                    marker.style.top = `calc(50% + ${verticalOffset}px)`;
                    
                    // Add tooltip data with day number included
                    marker.dataset.name = bill.name;
                    marker.dataset.amount = formatCurrency(bill.amount);
                    marker.dataset.date = `Day ${bill.dueDate}`;
                    
                    // Set color based on category
                    marker.style.backgroundColor = categoryColors[bill.category] || '#62B6CB';
                    
                    dateGroup.appendChild(marker);
                });
                
                // We're removing the date indicator at the bottom as requested
                timelineMarkers.appendChild(dateGroup);
            } else {
                // Single bill on this date - use the standard display
                const bill = dateBills[0];
                const marker = document.createElement('div');
                marker.className = 'timeline-marker';
                marker.style.left = `${datePosition}%`;
                
                marker.dataset.name = bill.name;
                marker.dataset.amount = formatCurrency(bill.amount);
                marker.dataset.date = `Day ${bill.dueDate}`;
                
                marker.style.backgroundColor = categoryColors[bill.category] || '#62B6CB';
                
                timelineMarkers.appendChild(marker);
            }
        });
        
        // Add legend
        const usedCategories = new Set();
        billsWithDueDate.forEach(bill => {
            usedCategories.add(bill.category);
        });
        
        // Create or update legend
        let legendContainer = document.querySelector('.timeline-legend');
        if (!legendContainer) {
            legendContainer = document.createElement('div');
            legendContainer.className = 'timeline-legend';
            timelineMarkers.parentNode.appendChild(legendContainer);
        } else {
            legendContainer.innerHTML = '';
        }
        
        // Add legend items for used categories
        usedCategories.forEach(category => {
            const legendItem = document.createElement('div');
            legendItem.className = 'legend-item';
            
            const colorBox = document.createElement('span');
            colorBox.className = 'legend-color';
            colorBox.style.backgroundColor = categoryColors[category] || '#62B6CB';
            
            const categoryName = document.createElement('span');
            categoryName.textContent = getCategoryName(category);
            
            legendItem.appendChild(colorBox);
            legendItem.appendChild(categoryName);
            legendContainer.appendChild(legendItem);
        });
    }
    
    // Chart instance variable - moved outside function scope to maintain state
    let billsChart = null;
    
    // Initialize and update the chart
    function updateChart() {
        console.log('updateChart called');
        
        const chartElement = document.getElementById('billsChart');
        const showPercentages = document.getElementById('showPercentages').checked;
        
        if (!chartElement) {
            console.error('Chart canvas element not found');
            return;
        }
        
        let ctx;
        try {
            ctx = chartElement.getContext('2d');
            console.log('Canvas context created successfully');
        } catch (e) {
            console.error('Error getting canvas context:', e);
            return;
        }
        
        // Debug element existence
        console.log('Chart canvas found:', chartElement);
        
        // Destroy previous chart if it exists
        if (billsChart) {
            console.log('Destroying previous chart instance');
            billsChart.destroy();
        }
        
        // Check if there are any bills
        if (bills.length === 0) {
            // Display a message when no bills exist
            console.log('No bills, showing placeholder');
            chartElement.style.display = 'none';
            
            // Create or update the placeholder message with donut chart outline
            let placeholder = document.getElementById('chart-placeholder');
            if (!placeholder) {
                placeholder = document.createElement('div');
                placeholder.id = 'chart-placeholder';
                placeholder.className = 'chart-placeholder';
                placeholder.innerHTML = `
                    <div class="empty-chart-message">
                        <div class="donut-chart-placeholder">
                            <svg xmlns="http://www.w3.org/2000/svg" width="120" height="120" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
                                <circle cx="12" cy="12" r="10" stroke="#ddd" stroke-width="2" fill="none"></circle>
                                <circle cx="12" cy="12" r="5" stroke="#ddd" stroke-width="2" fill="none"></circle>
                                <path d="M12 2a10 10 0 0 1 10 10" stroke="#5FA8D3" stroke-width="2"></path>
                            </svg>
                            <div class="placeholder-text">
                                <h4>No Bills Yet</h4>
                                <p>Add bills to see your spending breakdown</p>
                            </div>
                        </div>
                    </div>
                `;
                chartElement.parentNode.appendChild(placeholder);
            } else {
                placeholder.style.display = 'block';
            }
            return;
        }
        
        // If there are bills, hide the placeholder and show the canvas
        const placeholder = document.getElementById('chart-placeholder');
        if (placeholder) {
            placeholder.style.display = 'none';
        }
        chartElement.style.display = 'block';
        
        // Create category totals with thorough validation
        const categoryTotals = {};
        
        // Initialize all possible categories with zero to ensure we have entries for all categories
        const allCategories = ['housing', 'utilities', 'transportation', 'entertainment', 'insurance', 'subscriptions', 'other'];
        allCategories.forEach(cat => {
            categoryTotals[cat] = 0;
        });
        
        // Add up bill amounts by category
        bills.forEach(bill => {
            if (bill && bill.category && typeof bill.amount === 'number') {
                categoryTotals[bill.category] += bill.amount;
            }
        });
        
        // Create labels and data arrays for the chart - only include categories with non-zero values
        const filteredCategories = Object.entries(categoryTotals)
            .filter(([key, value]) => value > 0)
            .reduce((obj, [key, value]) => {
                obj[key] = value;
                return obj;
            }, {});
            
        const labels = Object.keys(filteredCategories).map(key => getCategoryName(key));
        const data = Object.values(filteredCategories);
        
        // Category colors
        const categoryColors = [
            '#FF9800', // Housing
            '#4CAF50', // Utilities
            '#2196F3', // Transportation
            '#9C27B0', // Entertainment
            '#607D8B', // Insurance
            '#E91E63', // Subscriptions
            '#795548'  // Other
        ];
        
        // Calculate total amount for center text
        const totalAmount = data.reduce((sum, val) => sum + val, 0);
        
        // Debug the chart data
        console.log('Creating chart with data:', { labels, data });
        
        try {
            // Create a new canvas element to replace the existing one
            // This helps resolve potential issues with canvas state
            const oldCanvas = chartElement;
            const newCanvas = document.createElement('canvas');
            newCanvas.id = 'billsChart';
            newCanvas.width = oldCanvas.width;
            newCanvas.height = oldCanvas.height;
            oldCanvas.parentNode.replaceChild(newCanvas, oldCanvas);
            
            const freshCtx = newCanvas.getContext('2d');
            console.log('Fresh context created');
            
            // Map categories to their keys for icon lookup
            const categoryKeys = labels.map(label => {
                // Convert back to keys (lowercase and remove spaces)
                for (const [key, value] of Object.entries({
                    housing: 'Housing',
                    utilities: 'Utilities',
                    transportation: 'Transportation',
                    entertainment: 'Entertainment',
                    insurance: 'Insurance',
                    subscriptions: 'Subscriptions',
                    other: 'Other'
                })) {
                    if (value === label) return key;
                }
                return 'other'; // Default fallback
            });
            
            // Create the chart - ensuring it's a donut chart with proper styling
            billsChart = new Chart(freshCtx, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: data,
                        backgroundColor: categoryColors.slice(0, labels.length),
                        borderWidth: 2,
                        borderColor: '#ffffff',
                        hoverBorderWidth: 3,
                        hoverBorderColor: '#ffffff',
                        cutout: '70%',  // Make it a donut chart with proper hole size
                        hoverOffset: 8,
                        borderRadius: 3  // Rounded edges for a more modern look
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        tooltip: {
                            callbacks: {
                                title: function(context) {
                                    // Returns the category name with capitalized first letter
                                    return context[0].label;
                                },
                                label: function(context) {
                                    const value = context.raw;
                                    const total = context.dataset.data.reduce((sum, val) => sum + val, 0);
                                    return `Amount: ${formatCurrency(value)}`;
                                },
                                afterLabel: function(context) {
                                    // Only show percentage if toggle is checked
                                    if (showPercentages) {
                                        const value = context.raw;
                                        const total = context.dataset.data.reduce((sum, val) => sum + val, 0);
                                        const percentage = ((value / total) * 100).toFixed(1);
                                        return `Percentage: ${percentage}% of total`;
                                    }
                                    return null;
                                }
                            },
                            backgroundColor: 'rgba(27, 73, 101, 0.9)',
                            titleFont: {
                                size: 14,
                                family: "'Montserrat', sans-serif",
                                weight: 'bold'
                            },
                            bodyFont: {
                                size: 13,
                                family: "'Open Sans', sans-serif"
                            },
                            padding: 14,
                            cornerRadius: 8,
                            displayColors: true,
                            boxPadding: 6
                        },
                        legend: {
                            display: false // Hide built-in legend since we're using custom one
                        }
                    },
                    animation: {
                        animateScale: true,
                        animateRotate: true
                    }
                }
            });
            console.log('Chart created successfully');
        } catch (error) {
            console.error('Error creating chart:', error);
            
            // Fallback to a simple visualization if Chart.js fails
            createFallbackChart(labels, data, categoryColors.slice(0, labels.length), totalAmount);
        }
        
        // Function to create a simple HTML/CSS chart as a fallback
        function createFallbackChart(labels, data, colors, total) {
            console.log('Creating fallback chart visualization');
            const chartContainer = document.querySelector('.chart-container');
            
            // Clear the container
            chartContainer.innerHTML = '';
            
            // Create a simple donut chart using HTML/CSS
            const fallbackChart = document.createElement('div');
            fallbackChart.className = 'fallback-chart';
            fallbackChart.style.position = 'relative';
            fallbackChart.style.width = '250px';
            fallbackChart.style.height = '250px';
            fallbackChart.style.borderRadius = '50%';
            fallbackChart.style.background = 'conic-gradient(';
            
            // Calculate percentages and create the conic gradient
            let totalValue = data.reduce((sum, val) => sum + val, 0);
            let cumulativePercent = 0;
            
            // Create conic gradient string
            const segments = [];
            data.forEach((value, index) => {
                const percent = (value / totalValue) * 100;
                const color = colors[index];
                
                segments.push(`${color} ${cumulativePercent}% ${cumulativePercent + percent}%`);
                cumulativePercent += percent;
            });
            
            // Apply the gradient
            fallbackChart.style.background = `conic-gradient(${segments.join(', ')})`;
            
            // Add center circle for donut effect
            const centerCircle = document.createElement('div');
            centerCircle.style.position = 'absolute';
            centerCircle.style.width = '60%';
            centerCircle.style.height = '60%';
            centerCircle.style.background = 'white';
            centerCircle.style.borderRadius = '50%';
            centerCircle.style.top = '20%';
            centerCircle.style.left = '20%';
            centerCircle.style.display = 'flex';
            centerCircle.style.flexDirection = 'column';
            centerCircle.style.justifyContent = 'center';
            centerCircle.style.alignItems = 'center';
            
            // Add total amount text
            const totalText = document.createElement('div');
            totalText.className = 'center-text-amount';
            totalText.textContent = formatCurrency(total);
            
            const labelText = document.createElement('div');
            labelText.className = 'center-text-label';
            labelText.textContent = 'Total';
            
            centerCircle.appendChild(totalText);
            centerCircle.appendChild(labelText);
            fallbackChart.appendChild(centerCircle);
            
            // Add chart legend
            const legend = document.createElement('div');
            legend.className = 'fallback-legend';
            legend.style.marginTop = '20px';
            legend.style.display = 'flex';
            legend.style.flexWrap = 'wrap';
            legend.style.justifyContent = 'center';
            
            labels.forEach((label, index) => {
                const legendItem = document.createElement('div');
                legendItem.style.display = 'flex';
                legendItem.style.alignItems = 'center';
                legendItem.style.margin = '5px 10px';
                
                const colorBox = document.createElement('span');
                colorBox.style.display = 'inline-block';
                colorBox.style.width = '12px';
                colorBox.style.height = '12px';
                colorBox.style.backgroundColor = colors[index];
                colorBox.style.marginRight = '5px';
                colorBox.style.borderRadius = '2px';
                
                const labelSpan = document.createElement('span');
                labelSpan.textContent = `${label} (${((data[index] / totalValue) * 100).toFixed(1)}%)`;
                
                legendItem.appendChild(colorBox);
                legendItem.appendChild(labelSpan);
                legend.appendChild(legendItem);
            });
            
            // Append to container
            const chartWrapper = document.createElement('div');
            chartWrapper.style.display = 'flex';
            chartWrapper.style.flexDirection = 'column';
            chartWrapper.style.alignItems = 'center';
            chartWrapper.appendChild(fallbackChart);
            chartWrapper.appendChild(legend);
            
            chartContainer.appendChild(chartWrapper);
        }
        
        // Add center text with total amount
        try {
            // Get the freshly created canvas element
            const newCanvas = document.getElementById('billsChart');
            const chartContainer = newCanvas.parentNode;
            
            // Add center text
            let centerText = document.getElementById('chart-center-text');
            if (!centerText) {
                centerText = document.createElement('div');
                centerText.id = 'chart-center-text';
                centerText.className = 'chart-center-text';
                chartContainer.appendChild(centerText);
            }
            
            centerText.innerHTML = `
                <div class="center-text-amount">${formatCurrency(totalAmount)}</div>
                <div class="center-text-label">Total</div>
            `;
            
            // Create custom legend with icons
            const legendContainer = document.getElementById('chartLegend');
            if (legendContainer) {
                // Clear previous legend
                legendContainer.innerHTML = '';
                
                // Add legend items for each category
                labels.forEach((label, i) => {
                    // Find the category key
                    let categoryKey = 'other';
                    for (const [key, value] of Object.entries({
                        housing: 'Housing',
                        utilities: 'Utilities',
                        transportation: 'Transportation',
                        entertainment: 'Entertainment',
                        insurance: 'Insurance',
                        subscriptions: 'Subscriptions',
                        other: 'Other'
                    })) {
                        if (value === label) {
                            categoryKey = key;
                            break;
                        }
                    }
                    
                    // Create legend item
                    const item = document.createElement('div');
                    item.className = 'legend-item';
                    
                    // Create icon container with the category color
                    const iconContainer = document.createElement('div');
                    iconContainer.className = 'legend-icon';
                    iconContainer.style.color = categoryColors.slice(0, labels.length)[i];
                    
                    // Add SVG icon based on category
                    if (categoryIcons[categoryKey]) {
                        iconContainer.innerHTML = categoryIcons[categoryKey];
                    }
                    
                    // Create label text
                    const textContainer = document.createElement('span');
                    textContainer.className = 'legend-label';
                    
                    // Add percentage if toggle is on
                    const percentage = showPercentages ? 
                        ` (${((data[i] / data.reduce((a, b) => a + b, 0)) * 100).toFixed(1)}%)` : '';
                    textContainer.textContent = label + percentage;
                    
                    // Add all elements to legend
                    item.appendChild(iconContainer);
                    item.appendChild(textContainer);
                    legendContainer.appendChild(item);
                });
            }
            
            console.log('Center text and custom legend added successfully');
        } catch (error) {
            console.error('Error adding center text or legend:', error);
        }
    }
    
    // Add event listener for percentage toggle
    const percentageToggle = document.getElementById('showPercentages');
    if (percentageToggle) {
        percentageToggle.addEventListener('change', () => {
            // Update the chart when toggle changes
            updateChart();
        });
    }
});
