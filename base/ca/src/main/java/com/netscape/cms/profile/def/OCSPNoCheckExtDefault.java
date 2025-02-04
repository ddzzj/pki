// --- BEGIN COPYRIGHT BLOCK ---
// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; version 2 of the License.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License along
// with this program; if not, write to the Free Software Foundation, Inc.,
// 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
//
// (C) 2007 Red Hat, Inc.
// All rights reserved.
// --- END COPYRIGHT BLOCK ---
package com.netscape.cms.profile.def;

import java.util.Locale;

import org.mozilla.jss.netscape.security.extensions.OCSPNoCheckExtension;
import org.mozilla.jss.netscape.security.x509.X509CertInfo;

import com.netscape.certsrv.profile.EProfileException;
import com.netscape.certsrv.property.Descriptor;
import com.netscape.certsrv.property.EPropertyException;
import com.netscape.certsrv.property.IDescriptor;
import com.netscape.certsrv.request.IRequest;
import com.netscape.cmscore.apps.CMS;

/**
 * This class implements an enrollment default policy
 * that populates an OCSP No Check extension
 * into the certificate template.
 *
 * @version $Revision$, $Date$
 */
public class OCSPNoCheckExtDefault extends EnrollExtDefault {

    public static org.slf4j.Logger logger = org.slf4j.LoggerFactory.getLogger(OCSPNoCheckExtDefault.class);

    public static final String CONFIG_CRITICAL = "ocspNoCheckCritical";

    public static final String VAL_CRITICAL = "ocspNoCheckCritical";

    public OCSPNoCheckExtDefault() {
        super();
        addValueName(VAL_CRITICAL);
        addConfigName(CONFIG_CRITICAL);
    }

    @Override
    public IDescriptor getConfigDescriptor(Locale locale, String name) {
        if (name.equals(CONFIG_CRITICAL)) {
            return new Descriptor(IDescriptor.BOOLEAN, null,
                    "false",
                    CMS.getUserMessage(locale, "CMS_PROFILE_CRITICAL"));
        }
        return null;
    }

    @Override
    public IDescriptor getValueDescriptor(Locale locale, String name) {
        if (name.equals(VAL_CRITICAL)) {
            return new Descriptor(IDescriptor.BOOLEAN, null,
                    "false",
                    CMS.getUserMessage(locale, "CMS_PROFILE_CRITICAL"));
        }
        return null;
    }

    @Override
    public void setValue(String name, Locale locale,
            X509CertInfo info, String value)
            throws EPropertyException {
        if (name == null) {
            throw new EPropertyException(CMS.getUserMessage(
                        locale, "CMS_INVALID_PROPERTY", name));
        }

        OCSPNoCheckExtension ext = (OCSPNoCheckExtension)
                getExtension(OCSPNoCheckExtension.OID, info);

        if (ext == null) {
            try {
                populate(null, info);

            } catch (EProfileException e) {
                throw new EPropertyException(CMS.getUserMessage(
                        locale, "CMS_INVALID_PROPERTY", name));
            }

        }

        if (name.equals(VAL_CRITICAL)) {
            ext = (OCSPNoCheckExtension)
                    getExtension(OCSPNoCheckExtension.OID, info);
            boolean val = Boolean.parseBoolean(value);

            if (ext == null) {
                return;
            }
            ext.setCritical(val);
        } else {
            throw new EPropertyException(CMS.getUserMessage(
                        locale, "CMS_INVALID_PROPERTY", name));
        }
    }

    @Override
    public String getValue(String name, Locale locale,
            X509CertInfo info)
            throws EPropertyException {
        if (name == null) {
            throw new EPropertyException(CMS.getUserMessage(
                        locale, "CMS_INVALID_PROPERTY", name));
        }

        OCSPNoCheckExtension ext = (OCSPNoCheckExtension)
                getExtension(OCSPNoCheckExtension.OID, info);

        if (ext == null) {
            try {
                populate(null, info);

            } catch (EProfileException e) {
                throw new EPropertyException(CMS.getUserMessage(
                        locale, "CMS_INVALID_PROPERTY", name));
            }

        }

        if (name.equals(VAL_CRITICAL)) {
            ext = (OCSPNoCheckExtension)
                    getExtension(OCSPNoCheckExtension.OID, info);

            if (ext == null) {
                return null;
            }
            return ext.isCritical() ? "true" : "false";
        }
        throw new EPropertyException(CMS.getUserMessage(
                    locale, "CMS_INVALID_PROPERTY", name));
    }

    @Override
    public String getText(Locale locale) {
        return CMS.getUserMessage(locale, "CMS_PROFILE_DEF_OCSP_NO_CHECK_EXT",
                getConfig(CONFIG_CRITICAL));
    }

    /**
     * Populates the request with this policy default.
     */
    @Override
    public void populate(IRequest request, X509CertInfo info)
            throws EProfileException {
        OCSPNoCheckExtension ext = createExtension();

        addExtension(OCSPNoCheckExtension.OID, ext, info);
    }

    public OCSPNoCheckExtension createExtension() {
        OCSPNoCheckExtension ext = null;

        try {
            ext = new OCSPNoCheckExtension();
        } catch (Exception e) {
            logger.warn("OCSPNoCheckExtDefault:  createExtension " + e.getMessage(), e);
            return null;
        }
        boolean critical = getConfigBoolean(CONFIG_CRITICAL);

        ext.setCritical(critical);
        return ext;
    }
}
