# GitHub Pages Deployment Instructions - Edukultur AI Demos

**Task:** Deploy the Edukultur AI demo website to GitHub Pages for public access

**Developer:** [Intern Name]  
**Project:** Edukultur AI Interactive Demos  
**Estimated Time:** 30-60 minutes  

---

## 📋 Prerequisites

Before starting, ensure you have:
- [ ] GitHub account (if not, create one at [github.com](https://github.com))
- [ ] Git installed on your computer ([Download Git](https://git-scm.com/downloads))
- [ ] Access to the demo files in: `C:\Users\legon\Documents\Taktis\Client\Edukultur\Apps\demo`

---

## 🚀 Step-by-Step Deployment Guide

### Step 1: Create GitHub Repository

1. **Go to GitHub.com** and sign in
2. **Click "New repository"** (green button on homepage or "+" icon)
3. **Repository settings:**
   - Repository name: `edukultur-ai-demos`
   - Description: `Interactive AI-powered educational demos for language learning`
   - Set to **Public** (required for free GitHub Pages)
   - ✅ Check "Add a README file"
   - ✅ Check "Add .gitignore" and select "Node" or "Web"
   - Leave "Choose a license" as "None"
4. **Click "Create repository"**

### Step 2: Clone Repository to Local Computer

1. **Copy the repository URL:**
   - On your new repository page, click the green "Code" button
   - Copy the HTTPS URL (should look like: `https://github.com/yourusername/edukultur-ai-demos.git`)

2. **Open Command Prompt or PowerShell:**
   - Press `Win + R`, type `cmd`, press Enter
   - Navigate to a suitable folder (e.g., `cd C:\Users\legon\Documents`)

3. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/edukultur-ai-demos.git
   cd edukultur-ai-demos
   ```

### Step 3: Copy Demo Files

1. **Copy all demo files** from the source folder to your repository:
   - Source: `C:\Users\legon\Documents\Taktis\Client\Edukultur\Apps\demo`
   - Destination: Your cloned repository folder

2. **Files to copy:**
   ```
   ├── index.html
   ├── english alphabet spelling/
   │   ├── english-spelling.html
   │   ├── https_server.py
   │   ├── server.crt
   │   ├── server.key
   │   └── start_https_server.bat
   └── hanzi/
       ├── hanzi-handwriting.html
       ├── hanzilookup.min.js
       ├── mmah.json
       └── hanzilookup-analysis.md
   ```

3. **Verify file structure** in your repository folder matches above

### Step 4: Commit and Push Files

1. **Add all files to git:**
   ```bash
   git add .
   ```

2. **Commit the changes:**
   ```bash
   git commit -m "Initial deployment: Add Edukultur AI demos with homepage and interactive demos"
   ```

3. **Push to GitHub:**
   ```bash
   git push origin main
   ```

### Step 5: Enable GitHub Pages

1. **Go to your repository** on GitHub.com
2. **Click "Settings"** tab (top navigation)
3. **Scroll down to "Pages"** section (left sidebar)
4. **Source settings:**
   - Source: Select "Deploy from a branch"
   - Branch: Select "main"
   - Folder: Select "/ (root)"
5. **Click "Save"**

6. **Wait for deployment:**
   - GitHub will show a message: "Your site is ready to be published at..."
   - Initial deployment takes 5-10 minutes
   - You'll get a green checkmark when ready

### Step 6: Test the Deployed Site

1. **Find your site URL:**
   - Go to Settings > Pages
   - Your URL will be: `https://yourusername.github.io/edukultur-ai-demos/`

2. **Test all functionality:**
   - [ ] Homepage loads correctly
   - [ ] Dark/light theme toggle works
   - [ ] "English Spelling Demo" button works
   - [ ] "Hanzi Writing Demo" button works
   - [ ] Both demo pages load without errors
   - [ ] "Back to Homepage" buttons work
   - [ ] Hanzi demo can load JSON file (CORS issue should be resolved)

---

## 🔧 Troubleshooting

### Common Issues and Solutions:

**Issue: "Repository not found" when cloning**
- **Solution:** Check you copied the correct URL and have access to the repository

**Issue: "Permission denied" when pushing**
- **Solution:** 
  1. Check you're logged into the correct GitHub account
  2. Try: `git remote set-url origin https://yourusername:yourtoken@github.com/yourusername/edukultur-ai-demos.git`

**Issue: GitHub Pages shows 404 error**
- **Solution:** 
  1. Ensure `index.html` is in the root directory
  2. Wait 5-10 minutes for GitHub to build the site
  3. Check the Actions tab for any build errors

**Issue: Hanzi demo still doesn't work**
- **Solution:** 
  1. Check browser developer console for errors
  2. Ensure `mmah.json` file was uploaded correctly
  3. Verify file size (should be ~827KB)

**Issue: Styling looks wrong**
- **Solution:**
  1. Hard refresh the page (Ctrl+F5)
  2. Check browser developer tools for any 404 errors on resources

---

## 📝 Final Checklist

Before marking the task complete, verify:

- [ ] Repository created successfully
- [ ] All files uploaded to GitHub
- [ ] GitHub Pages enabled and deployed
- [ ] Site accessible at public URL
- [ ] Homepage works correctly
- [ ] Both demos are functional
- [ ] Navigation between pages works
- [ ] Theme toggle functions properly
- [ ] No console errors in browser developer tools

---

## 🎯 Expected Result

After successful deployment:

1. **Public URL:** `https://yourusername.github.io/edukultur-ai-demos/`
2. **Homepage:** Professional landing page with two demo cards
3. **English Demo:** Fully functional spelling practice with voice recognition
4. **Hanzi Demo:** Working Chinese character handwriting recognition
5. **Responsive:** Works on desktop, tablet, and mobile devices

---

## 📞 Support

If you encounter any issues:

1. **Check the GitHub repository Actions tab** for build errors
2. **Review browser developer console** for JavaScript errors
3. **Compare your file structure** with the instructions above
4. **Document any errors** with screenshots for further assistance

---

**Deployment Date:** [Fill in when completed]  
**Public URL:** [Fill in the actual URL when deployed]  
**Status:** [Pending/In Progress/Completed]

---

## 🏆 Success Criteria

The deployment is successful when:
- ✅ Site loads without errors at the public GitHub Pages URL
- ✅ All interactive features work as expected
- ✅ Both English and Hanzi demos are fully functional
- ✅ Design matches the taktis.in inspired styling
- ✅ Site is responsive across different devices
- ✅ No CORS errors in the browser console